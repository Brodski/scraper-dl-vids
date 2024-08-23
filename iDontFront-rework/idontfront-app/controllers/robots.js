exports.robots = async (req, res) => {
    res.type('text/plain')
    res.send(`User-agent: *
Disallow:

Sitemap: ${process.env.URL_CANONICAL_BASE}/sitemap.xml`);
}