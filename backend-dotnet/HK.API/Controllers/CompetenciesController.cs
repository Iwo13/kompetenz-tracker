using Microsoft.AspNetCore.Mvc;

namespace HK.API.Controllers;

[ApiController]
[Route("[controller]")]
public class CompetenciesController(IConfiguration config) : ControllerBase
{
    [HttpGet("{name}")]
    public IActionResult GetByName(string name)
    {
        var dir  = config["DataPaths:CompetenciesDir"] ?? "../../data";
        var path = Path.GetFullPath(Path.Combine(Directory.GetCurrentDirectory(), dir, $"{name}.json"));

        if (!System.IO.File.Exists(path))
            return NotFound(new { detail = "Kompetenz-Datei nicht gefunden" });

        var json = System.IO.File.ReadAllText(path, System.Text.Encoding.UTF8);
        return Content(json, "application/json");
    }
}
