// Mock data for Wings of Capital dashboard
window.WOC_DATA = {
  user: { name: "George", theme_preference: "dark" },
  metrics: {
    ai_insight: "Your Transaction Volume has increased by 5% Since last Month",
    balance: {
      current: 17241.00,
      delta_percentage: 12,
      total_transactions: 44,
      categories: 12,
      timeseries: [
        { date: "16", value: 15000 },
        { date: "17", value: 15320 },
        { date: "18", value: 15700 },
        { date: "19", value: 16000 },
        { date: "20", value: 16500 },
        { date: "21", value: 16800 },
        { date: "22", value: 17000 },
        { date: "23", value: 17241 }
      ]
    },
    earnings: {
      current: 6400.00,
      delta_percentage: 7,
      goal_percentage: 58
    },
    spending: {
      current: 2000.00,
      delta_percentage: -2,
      categories: {
        Clothing: 400,
        Groceries: 800,
        Pets: 200,
        Bills: 600
      }
    }
  },
  recent_transactions: [
    { merchant: "PlayStation", card_last_four: "0224", timestamp: "31 Mar, 3:20 PM", amount: -19.99 },
    { merchant: "Netflix", card_last_four: "0224", timestamp: "29 Mar, 5:11 PM", amount: -30.00 },
    { merchant: "Airbnb", card_last_four: "4432", timestamp: "28 Mar, 1:20 PM", amount: -300.00 },
    { merchant: "Tommy C.", card_last_four: "0224", timestamp: "27 Mar, 2:31 AM", amount: 2700.00 },
    { merchant: "Apple", card_last_four: "4432", timestamp: "27 Mar, 11:04 PM", amount: -10.00 }
  ]
};
