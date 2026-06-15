# AdSense Setup Guide for freeconvert.cloud

Your site is now AdSense-ready. Follow these steps after Google approves your AdSense account.

## Step 1 — Create Real Ad Units
1. Log in to [Google AdSense](https://www.google.com/adsense/).
2. Go to **Ads → Overview → By ad unit**.
3. Create these Display ad units (all responsive):
   - `REPLACE_SLOT_HOME_TOP` — Homepage below hero
   - `REPLACE_SLOT_CAT_TOP` — Category page mid-content
   - `REPLACE_SLOT_MID_CONTENT` — Tool page after how-to
   - `REPLACE_SLOT_FOOTER` — Footer sponsored links
   - `REPLACE_SLOT_LEGAL_MID` — Legal/policy pages mid-content
   - `REPLACE_SLOT_BLOG_TOP` — Blog hub page top
4. Copy each **Ad slot ID** (a 10-digit number like `1234567890`).

## Step 2 — Replace Placeholder Slot IDs
Search and replace across all `index.html` files:

```text
REPLACE_SLOT_HOME_TOP      → your real home-top slot ID
REPLACE_SLOT_CAT_TOP       → your real category slot ID
REPLACE_SLOT_MID_CONTENT   → your real mid-content slot ID
REPLACE_SLOT_FOOTER        → your real footer slot ID
REPLACE_SLOT_LEGAL_MID     → your real legal-page slot ID
REPLACE_SLOT_BLOG_TOP      → your real blog-hub slot ID
```

If you rebuild with `build_tools.py`, update the slot IDs inside `build_tools.py` and `tools/tool-template.html` first, then regenerate.

## Step 3 — Enable Ads
All ad wrappers are hidden by `adsense-review.css` until you tell the site ads are live.

### Option A — Add a body class (recommended)
Add this script right before `</body>` on every page, or in a shared footer file:

```html
<script>
// Show AdSense ad containers once the AdSense script has loaded
(function() {
  function showAds() {
    document.body.classList.add('ads-enabled');
  }
  if (window.adsbygoogle && window.adsbygoogle.loaded) {
    showAds();
  } else {
    window.addEventListener('load', function() {
      setTimeout(showAds, 1500);
    });
  }
})();
</script>
```

Or simply change `<body>` to `<body class="ads-enabled">` in `tools/tool-template.html` and rebuild after approval.

### Option B — Remove the hiding rule
Edit `adsense-review.css` and delete or comment out these lines:

```css
body:not(.ads-enabled) .adsense-placeholder-wrap,
body:not(.ads-enabled) .adsense-wrap {
    display: none !important;
}
```

## Step 4 — Verify
- Open any tool page in an incognito browser.
- Inspect an ad wrapper. It should be visible and contain an `<ins class="adsbygoogle">` element.
- Check the browser console for AdSense errors.
- Wait 24–48 hours for Google to start serving ads.

## Policy Reminders
- Keep the `ads.txt` file at the root exactly as it is.
- Do **not** place ads over tool buttons, upload boxes, or action areas.
- Do **not** encourage accidental clicks.
- Ensure `advertising-policy/` page stays linked in the footer.

## Already Done for You
- AdSense verification script is in the `<head>` of every page.
- Ad preconnect/dns-prefetch hints are added for faster loading.
- Responsive ad units are placed in high-viewability positions.
- Empty ad placeholders are hidden by CSS until you enable them.
