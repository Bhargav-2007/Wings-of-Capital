// Fetch wrapper with token injection and retry
window.WOC_HTTP = async function(url, opts = {}, retries = 2) {
  opts.headers = opts.headers || {};
  const token = localStorage.getItem('token');
  if (token) opts.headers['Authorization'] = 'Bearer ' + token;
  try {
    const res = await fetch(url, opts);
    if (!res.ok && retries > 0) {
      return await window.WOC_HTTP(url, opts, retries - 1);
    }
    return res;
  } catch (e) {
    if (retries > 0) return await window.WOC_HTTP(url, opts, retries - 1);
    throw e;
  }
};
