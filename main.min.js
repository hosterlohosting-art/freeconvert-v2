document.addEventListener("DOMContentLoaded", async () => {
    // Mobile nav toggle.
    const navToggle = document.getElementById("mobile-toggle") || document.querySelector(".mobile-toggle");
    const navLinks = document.querySelector(".nav-links");
    if (navToggle && navLinks) {
        navToggle.addEventListener("click", () => {
            navToggle.classList.toggle("active");
            navLinks.classList.toggle("active");
        });
    }
    document.querySelectorAll(".nav-link").forEach((link) => {
        link.addEventListener("click", () => {
            if (navToggle) navToggle.classList.remove("active");
            if (navLinks) navLinks.classList.remove("active");
        });
    });

    // Tools that must never appear in the grid or in search results: pages with
    // no working in-browser tool (video converters, Word/PDF converters,
    // barcode generator, speed test, and the hub pages that only list tools).
    // tools/tools.json is the clean source of truth (stubs removed there); this
    // list is defence in depth in case a stale cached copy still contains them.
    const HIDDEN_TOOL_IDS = new Set([
        "avi-to-mp4", "mkv-to-mp4", "mov-to-mp4", "webm-to-mp4",
        "mp4-to-gif", "mp4-to-mp3", "video-to-mp3", "video-compressor",
        "video-resizer", "video-trimmer", "pdf-to-word", "word-to-pdf",
        "ico-converter", "palette-extractor", "barcode-generator", "speed-test",
        "archive-converter", "audio-converter", "ebook-converter",
        "video-converter", "pdf-tools", "document-converter"
    ]);
    const isLiveTool = (tool) =>
        Boolean(tool && tool.id) && !HIDDEN_TOOL_IDS.has(tool.id) && tool.status !== "stub";

    // Normalise the category names used in tools.json to the homepage tab names.
    // "PDF Tools" gets its own tab; "Text" lives under the Utility tab.
    const tabOf = (tool) => {
        const category = (tool.category || "").toLowerCase();
        if (category === "pdf tools") return "pdf";
        if (category === "video converter") return "video";
        if (category === "text") return "utility";
        return category;
    };

    // Every word of the query must match the tool name, description, or slug,
    // so "split pdf", "pdf to jpg", and "jpg to pdf" all find their tool.
    const matchesQuery = (tool, query) => {
        if (!query) return true;
        const haystack = `${tool.name} ${tool.description} ${tool.id.replace(/-/g, " ")}`.toLowerCase();
        return query.split(/\s+/).every((word) => haystack.includes(word));
    };

    const searchInput = document.getElementById("tool-search");
    const mainGrid = document.querySelector("main.tool-grid");

    // Render one tool card in exactly the same markup as the static cards.
    const cardHtml = (tool) => `
            <a href="/${tool.id}/" class="tool-card" data-category="${tabOf(tool)}">
                <div class="tool-card-top">
                    <div class="tool-icon">${tool.icon}</div>
                    <span class="tool-category-tag">${tool.category}</span>
                </div>
                <div class="tool-card-body">
                    <span role="heading" aria-level="3" style="display:block;font-size:1.25rem;color:var(--text-primary);font-weight:800;margin-bottom:0.5rem;line-height:1.25;">${tool.name}</span>
                    <p>${tool.description}</p>
                </div>
                <div class="tool-card-footer">
                    <span class="explore-text">Explore Tool</span>
                    <span class="arrow-icon">→</span>
                </div>
            </a>`;

    if (mainGrid) {
        // Homepage: render the grid from tools/tools.json, the single source of
        // truth. A stale window.TOOLS_DATA (if present) is only a fallback when
        // the fetch fails, and it goes through the same live-tool filter.
        let tools = [];
        try {
            const response = await fetch("/tools/tools.json");
            const data = await response.json();
            tools = (Array.isArray(data) ? data : []).filter(isLiveTool);
        } catch (error) {
            console.error("Failed to load tools", error);
        }
        if (!tools.length && Array.isArray(window.TOOLS_DATA)) {
            tools = window.TOOLS_DATA.filter(isLiveTool);
        }

        let activeTab = "all";
        const render = () => {
            const query = searchInput ? searchInput.value.trim().toLowerCase() : "";
            const visible = tools.filter(
                (tool) => (activeTab === "all" || tabOf(tool) === activeTab) && matchesQuery(tool, query)
            );
            mainGrid.innerHTML = visible.length
                ? visible.map(cardHtml).join("")
                : '<p style="color:var(--text-muted); text-align:center; grid-column: 1/-1; padding:2rem 0;">No tools match that search. Try another file type or <a href="/all-tools/" style="color:var(--brand-primary);font-weight:700;">browse all tools</a>.</p>';
        };

        render();
        if (searchInput) searchInput.addEventListener("input", render);
        document.querySelectorAll(".category-tab").forEach((tab) => {
            tab.addEventListener("click", () => {
                document.querySelectorAll(".category-tab").forEach((t) => t.classList.remove("active"));
                tab.classList.add("active");
                activeTab = tab.getAttribute("data-category") || "all";
                render();
            });
        });
    } else if (searchInput) {
        // All Tools page: the cards are static, so filter them in place instead
        // of re-rendering. Empty sections are hidden; a note shows on no match.
        const cards = Array.from(document.querySelectorAll(".tool-card"));
        const grids = Array.from(document.querySelectorAll(".tool-grid"));
        const noResults = document.getElementById("all-tools-no-results");
        const applyFilter = () => {
            const query = searchInput.value.trim().toLowerCase();
            let visibleCount = 0;
            cards.forEach((card) => {
                const text = `${card.textContent} ${card.getAttribute("href") || ""}`.toLowerCase().replace(/-/g, " ");
                const hit = !query || query.split(/\s+/).every((word) => text.includes(word));
                card.style.display = hit ? "" : "none";
                if (hit) visibleCount++;
            });
            grids.forEach((grid) => {
                const section = grid.closest("section");
                if (!section) return;
                const anyVisible = Array.from(grid.querySelectorAll(".tool-card")).some(
                    (card) => card.style.display !== "none"
                );
                section.style.display = anyVisible ? "" : "none";
            });
            if (noResults) noResults.style.display = visibleCount ? "none" : "block";
        };
        searchInput.addEventListener("input", applyFilter);
    }
});
