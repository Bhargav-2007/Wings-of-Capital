// Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
// Licensed under the Apache License, Version 2.0.

/**
 * Wings of Capital — Chart Helpers
 * Utilities for generating dummy data and building dataset structures.
 */

'use strict';

const ChartHelpers = (() => {

  /** Generate random walk data for sparklines/demo charts */
  function generateRandomWalk(points, startValue, volatility) {
    const data = [startValue];
    let current = startValue;
    for (let i = 1; i < points; i++) {
      const change = (Math.random() - 0.5) * volatility;
      current = Math.max(0, current + change); // Don't go below 0
      data.push(current);
    }
    return data;
  }

  /** Generate last N days as labels */
  function generateDateLabels(days) {
    const labels = [];
    const today = new Date();
    for (let i = days - 1; i >= 0; i--) {
      const d = new Date(today);
      d.setDate(d.getDate() - i);
      labels.push(Fmt.date(d.toISOString()).split(',')[0]); // Just Mon DD
    }
    return labels;
  }
  
  /** 
   * Formats API portfolio data into DonutChart friendly structure 
   * Expects: { assets: [{ symbol: 'BTC', value_usd: 5000 }, ...] }
   */
  function formatAllocationData(portfolioData) {
      if(!portfolioData || !portfolioData.assets) return { labels: [], data: [] };
      
      // Sort by value descending
      const sorted = [...portfolioData.assets].sort((a,b) => b.value_usd - a.value_usd);
      
      return {
          labels: sorted.map(a => a.symbol),
          data: sorted.map(a => a.value_usd)
      };
  }

  return Object.freeze({
    generateRandomWalk,
    generateDateLabels,
    formatAllocationData
  });
})();
