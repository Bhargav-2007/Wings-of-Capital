// Simple GraphQL query builder
window.WOC_GraphQL = async function(url, query, variables = {}) {
  const res = await window.WOC_HTTP(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, variables })
  });
  return res.json();
};
