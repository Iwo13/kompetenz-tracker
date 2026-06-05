using System.Text.Json;
using System.Text.Json.Nodes;
using Microsoft.AspNetCore.Mvc;

namespace HK.API.Controllers;

[ApiController]
[Route("[controller]")]
public class AusbildungsplaetzeController(IConfiguration config) : ControllerBase
{
    private string ApFilePath =>
        Path.GetFullPath(Path.Combine(
            Directory.GetCurrentDirectory(),
            config["DataPaths:AusbildungsplaetzeFile"] ?? "../../backend/ausbildungsplaetze.json"
        ));

    private JsonObject LoadData()
    {
        var json = System.IO.File.ReadAllText(ApFilePath, System.Text.Encoding.UTF8);
        return JsonNode.Parse(json)!.AsObject();
    }

    private void SaveData(JsonObject data)
        => System.IO.File.WriteAllText(ApFilePath,
            data.ToJsonString(new JsonSerializerOptions { WriteIndented = true }),
            System.Text.Encoding.UTF8);

    private JsonObject? FindAp(JsonObject data, string code)
        => data["ausbildungsplaetze"]!.AsArray()
            .FirstOrDefault(n => n!["code"]!.GetValue<string>() == code)
            ?.AsObject();

    // GET /ausbildungsplaetze
    [HttpGet]
    public IActionResult GetAll()
    {
        var json = System.IO.File.ReadAllText(ApFilePath, System.Text.Encoding.UTF8);
        return Content(json, "application/json");
    }

    // POST /ausbildungsplaetze
    [HttpPost]
    public IActionResult Create([FromBody] JsonObject body)
    {
        var code = body["code"]?.GetValue<string>()?.Trim().ToUpperInvariant();
        if (string.IsNullOrEmpty(code))
            return BadRequest(new { detail = "Code fehlt" });

        var data = LoadData();
        var arr  = data["ausbildungsplaetze"]!.AsArray();

        if (arr.Any(n => n!["code"]!.GetValue<string>() == code))
            return Conflict(new { detail = "AP-Code bereits vorhanden" });

        var newAp = new JsonObject
        {
            ["code"]       = code,
            ["name"]       = body["name"]?.GetValue<string>() ?? code,
            ["abLehrjahr"] = body["abLehrjahr"]?.GetValue<int>() ?? 2,
            ["hk_coverage"] = new JsonObject
            {
                ["informatiker"]  = new JsonObject(),
                ["ict-fachmann"]  = new JsonObject(),
            },
        };
        arr.Add(newAp.DeepClone());
        SaveData(data);
        return CreatedAtAction(nameof(GetAll), null, newAp);
    }

    // PUT /ausbildungsplaetze/{code}/bereiche
    [HttpPut("{code}/bereiche")]
    public IActionResult UpdateBereiche(string code, [FromBody] JsonObject body)
    {
        var data = LoadData();
        var ap   = FindAp(data, code);
        if (ap is null) return NotFound(new { detail = "AP nicht gefunden" });

        var bereiche = body["bereiche"]?.AsObject() ?? new JsonObject();
        if (ap["bereiche"] is null) ap["bereiche"] = new JsonObject();
        foreach (var (k, v) in bereiche)
            ap["bereiche"]![k] = v?.DeepClone();

        SaveData(data);
        return Ok(ap);
    }

    // PUT /ausbildungsplaetze/{code}/hk
    [HttpPut("{code}/hk")]
    public IActionResult UpdateHk(string code, [FromBody] JsonObject body)
    {
        var data        = LoadData();
        var ap          = FindAp(data, code);
        if (ap is null) return NotFound(new { detail = "AP nicht gefunden" });

        var bildungsplan = body["bildungsplan"]!.GetValue<string>();
        var hkId         = body["hk_id"]!.GetValue<string>();
        var coverage     = body["coverage"]?.GetValue<string?>();

        if (ap["hk_coverage"] is null)        ap["hk_coverage"]        = new JsonObject();
        if (ap["hk_coverage"]![bildungsplan] is null) ap["hk_coverage"]![bildungsplan] = new JsonObject();
        ap["hk_coverage"]![bildungsplan]![hkId] = coverage is null ? null : JsonValue.Create(coverage);

        SaveData(data);
        return Ok(new { code, bildungsplan, hk_id = hkId, coverage });
    }
}
