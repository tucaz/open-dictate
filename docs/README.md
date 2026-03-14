# Website

Static GitHub Pages site for Open-Dictate Windows.

## Files

- `index.html`: landing page
- `styles.css`: site styles
- `script.js`: optional latest-release enhancement with a GitHub Releases fallback

## Deployment

Serve the `docs/` directory with GitHub Pages or any static host.

Notes:

- Links and assets use relative paths so the page works on a GitHub Pages project URL or a custom domain.
- The hero button links to the install section, while the ZIP links in the portable/manual-install cards fall back to GitHub Releases if the GitHub API request fails or JavaScript is disabled.
- If this repo later uses GitHub Pages Actions, publish the contents of `docs/` as the site root.
- Repository URLs in the site currently target `https://github.com/tucaz/open-dictate`.
