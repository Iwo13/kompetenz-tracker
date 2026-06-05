import { describe, it, expect } from 'vitest';
import {
  getInitials,
  getLehrjahrInfo,
  getAreaProgress,
  getOverallProgress,
} from './utils.js';

// ─── getInitials ────────────────────────────────────────────────────────────

describe('getInitials', () => {

  it('returns two uppercase initials for a full name', () => {
    // ARRANGE
    const name = 'Max Muster';
    // ACT
    const result = getInitials(name);
    // ASSERT
    expect(result).toBe('MM');
  });

  it('returns one initial for a single name', () => {
    // ARRANGE
    const name = 'Anna';
    // ACT
    const result = getInitials(name);
    // ASSERT
    expect(result).toBe('A');
  });

  it('returns empty string for an empty name', () => {
    // ARRANGE
    const name = '';
    // ACT
    const result = getInitials(name);
    // ASSERT
    expect(result).toBe('');
  });

});

// ─── getLehrjahrInfo ─────────────────────────────────────────────────────────

describe('getLehrjahrInfo', () => {

  it('returns lehrjahr 1 and 0 percent when no startDate is given', () => {
    // ARRANGE
    const user = { specialty: 'app' };
    // ACT
    const result = getLehrjahrInfo(user);
    // ASSERT
    expect(result.current).toBe(1);
    expect(result.pct).toBe(0);
  });

  it('uses 3 years duration for ict-fachmann specialty', () => {
    // ARRANGE
    const user = { specialty: 'ict-fachmann' };
    // ACT
    const result = getLehrjahrInfo(user);
    // ASSERT
    expect(result.lehrDauer).toBe(3);
  });

  it('uses 4 years duration for app specialty', () => {
    // ARRANGE
    const user = { specialty: 'app' };
    // ACT
    const result = getLehrjahrInfo(user);
    // ASSERT
    expect(result.lehrDauer).toBe(4);
  });

  it('returns lehrjahr 2 when start date is about 1 year ago', () => {
    // ARRANGE
    const oneYearAgo = new Date();
    oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);
    const user = { specialty: 'app', startDate: oneYearAgo.toISOString() };
    // ACT
    const result = getLehrjahrInfo(user);
    // ASSERT
    expect(result.current).toBe(2);
  });

});

// ─── getAreaProgress ─────────────────────────────────────────────────────────

describe('getAreaProgress', () => {

  it('returns 100 percent when all goals are achieved', () => {
    // ARRANGE
    const area = {
      subComps: [{ goals: [{ id: 'g1', max: 3 }, { id: 'g2', max: 2 }] }],
    };
    const userGoals = { g1: { level: 3 }, g2: { level: 2 } };
    // ACT
    const result = getAreaProgress(area, userGoals);
    // ASSERT
    expect(result.pct).toBe(100);
    expect(result.achieved).toBe(2);
    expect(result.total).toBe(2);
  });

  it('returns 0 percent when no goals are achieved', () => {
    // ARRANGE
    const area = {
      subComps: [{ goals: [{ id: 'g1', max: 3 }] }],
    };
    const userGoals = {};
    // ACT
    const result = getAreaProgress(area, userGoals);
    // ASSERT
    expect(result.pct).toBe(0);
    expect(result.achieved).toBe(0);
  });

  it('returns 50 percent when half the goals are achieved', () => {
    // ARRANGE
    const area = {
      subComps: [{ goals: [{ id: 'g1', max: 2 }, { id: 'g2', max: 2 }] }],
    };
    const userGoals = { g1: { level: 2 } };
    // ACT
    const result = getAreaProgress(area, userGoals);
    // ASSERT
    expect(result.pct).toBe(50);
  });

});

// ─── getOverallProgress ──────────────────────────────────────────────────────

describe('getOverallProgress', () => {

  it('returns 0 percent for empty areas', () => {
    // ARRANGE
    const areas = [];
    // ACT
    const result = getOverallProgress(areas, {});
    // ASSERT
    expect(result.pct).toBe(0);
    expect(result.total).toBe(0);
  });

  it('returns correct overall percentage across multiple areas', () => {
    // ARRANGE
    const areas = [
      { subComps: [{ goals: [{ id: 'g1', max: 1 }, { id: 'g2', max: 1 }] }] },
      { subComps: [{ goals: [{ id: 'g3', max: 1 }, { id: 'g4', max: 1 }] }] },
    ];
    const userGoals = { g1: { level: 1 }, g3: { level: 1 } }; // 2 of 4 achieved
    // ACT
    const result = getOverallProgress(areas, userGoals);
    // ASSERT
    expect(result.pct).toBe(50);
    expect(result.achieved).toBe(2);
    expect(result.total).toBe(4);
  });

});
