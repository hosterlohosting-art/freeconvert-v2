/**
 * Freeconvert.cloud Unified Conversion Engine Adapter
 * 
 * Provides an abstract architectural layer separating frontend UI states
 * from conversion execution drivers (client-side canvas vs. backend APIs).
 */

class ConversionEngineAdapter {
    constructor() {
        this.currentFile = null;
        this.config = {
            // Easily swap this URL with a real endpoint (e.g., CloudConvert, ConvertAPI, custom server)
            apiEndpoint: 'https://api.freeconvert.cloud/v1/convert',
            isBackendConnected: false // Set to true when backend API is live
        };
        
        // Define format mappings for input to output compatibility
        this.formatMappings = {
            'png': ['jpg', 'webp', 'pdf', 'ico', 'base64'],
            'jpg': ['png', 'webp', 'pdf', 'ico', 'base64'],
            'jpeg': ['png', 'webp', 'pdf', 'ico', 'base64'],
            'webp': ['jpg', 'png', 'pdf', 'base64'],
            'svg': ['png', 'jpg'],
            'heic': ['jpg', 'png'],
            'doc': ['docx', 'pdf', 'txt'],
            'docx': ['doc', 'pdf', 'txt'],
            'pdf': ['pdf', 'docx', 'doc', 'jpg', 'png', 'txt'],
            'mp4': ['mp4', 'mp3', 'wav', 'avi', 'mov', 'webm'],
            'mp3': ['wav', 'ogg', 'm4a', 'flac'],
            'webm': ['mp4', 'webm', 'avi', 'mov'],
            'txt': ['pdf', 'base64', 'binary', 'csv', 'json']
        };
    }

    /**
     * Resolve valid output formats based on input extension
     */
    getOutputFormats(fileName) {
        const ext = fileName.split('.').pop().toLowerCase();
        return this.formatMappings[ext] || ['pdf', 'zip', 'txt'];
    }

    /**
     * Executes the conversion lifecycle
     * @param {File} file Input file object
     * @param {string} targetFormat Target output extension
     * @param {Object} options Optional advanced adjustments (quality, width, etc.)
     * @returns {Promise<Blob|Object>} Output binary blob or data object
     */
    async convert(file, targetFormat, options = {}) {
        const fileExt = file.name.split('.').pop().toLowerCase();
        
        // --- ROUTING ENGINE ---
        // Determines if a task can run entirely inside the client's browser (0% server load, 100% private)
        // or if it requires a secure backend cluster (PDF parsing, Video re-encoding, ZIP compression, etc.)
        if (this.isClientSideTool(fileExt, targetFormat)) {
            return this.executeClientSideConversion(file, targetFormat, options);
        } else {
            return this.executeBackendConversion(file, targetFormat, options);
        }
    }

    /**
     * Helper to classify if a conversion can run 100% in-browser.
     * 
     * [CLIENT-SIDE BROWSER ONLY]:
     * - Web-friendly images (PNG, JPG, WebP, SVG, HEIC to JPG/PNG/WebP) using HTML5 Canvas.
     * - Developer converters (Base64 encoding/decoding, Binary conversions) using FileReader/String mapping.
     * - Interactive utilities (Word counter, stopwatch, aspect ratio, lorem generators) running local JS scripts.
     * 
     * [BACKEND-REQUIRED]:
     * - Documents (Word/DOC/DOCX, Excel/XLS/XLSX, PowerPoint/PPTX to PDF) using LibreOffice.
     * - Media transcoding (MP4 to MP3, WAV to FLAC, WebM re-encoding) using FFmpeg.
     * - File archives (ZIP extraction, RAR extraction, 7Z compression) using system-level zip utilities.
     * - eBook layout compilation (EPUB, MOBI, AZW3) using Calibre/ebook-convert engines.
     */
    isClientSideTool(sourceExt, targetExt) {
        const clientSideImages = ['png', 'jpg', 'jpeg', 'webp', 'svg', 'heic'];
        const isImageConvert = clientSideImages.includes(sourceExt) && clientSideImages.includes(targetExt);
        return isImageConvert || targetExt === 'base64' || targetExt === 'binary';
    }

    /**
     * Client-Side Web API & Canvas conversion driver.
     * Processes file binary directly in the device's sandbox environment.
     * 100% private, 0ms queue latency, mathematically secure.
     */
    async executeClientSideConversion(file, targetFormat, options) {
        return new Promise(async (resolve, reject) => {
            if (targetFormat === 'base64') {
                const reader = new FileReader();
                reader.onload = (e) => resolve(new Blob([e.target.result], {type: 'text/plain'}));
                reader.onerror = (e) => reject(e);
                reader.readAsDataURL(file);
                return;
            }

            // Image conversions using dynamic HTML5 Canvas rasterization
            const img = new Image();
            img.src = URL.createObjectURL(file);
            img.onload = async () => {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                
                let width = options.width || img.naturalWidth;
                let height = options.height || img.naturalHeight;
                
                const path = window.location.pathname.replace(/\//g, '');
                let sizeLimit = 0;
                if (path === 'compress-image-to-100kb') sizeLimit = 100 * 1024;
                if (path === 'compress-image-to-200kb') sizeLimit = 200 * 1024;
                
                let mimeType = 'image/png';
                if (targetFormat === 'jpg' || targetFormat === 'jpeg') mimeType = 'image/jpeg';
                if (targetFormat === 'webp') mimeType = 'image/webp';
                
                if (sizeLimit > 0 && mimeType === 'image/png') {
                    mimeType = 'image/jpeg'; // Force lossy mode for footprint limits
                }

                let currentQuality = options.quality ? parseFloat(options.quality) : 0.9;
                let scale = 1.0;
                
                const tryCompress = () => {
                    return new Promise((resBlob) => {
                        canvas.width = width * scale;
                        canvas.height = height * scale;
                        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                        canvas.toBlob((blob) => {
                            resBlob(blob);
                        }, mimeType, currentQuality);
                    });
                };
                
                try {
                    let blob = await tryCompress();
                    if (sizeLimit > 0) {
                        let attempts = 0;
                        while (blob && blob.size > sizeLimit && attempts < 15) {
                            attempts++;
                            if (currentQuality > 0.15) {
                                currentQuality -= 0.15;
                            } else {
                                scale *= 0.8;
                                currentQuality = 0.9;
                            }
                            blob = await tryCompress();
                        }
                    }
                    if (blob) {
                        resolve(blob);
                    } else {
                        reject(new Error('Canvas rasterization failed.'));
                    }
                } catch(err) {
                    reject(err);
                }
            };
            img.onerror = () => reject(new Error('Invalid image file.'));
        });
    }

    /**
     * Backend API gateway driver (CloudConvert, ConvertAPI, custom FFmpeg/LibreOffice server).
     * Automatically handles mock sandbox delays in Demo state, or forwards file payload to live endpoints.
     */
    async executeBackendConversion(file, targetFormat, options) {
        if (!this.config.isBackendConnected) {
            // [DEMO FALLBACK STATE]
            // Standard simulated progress to showcase premium, multi-stage loading flows
            // structured identically to async AJAX requests so transition to production is transparent.
            return new Promise((resolve) => {
                setTimeout(() => {
                    const mockBlob = new Blob([`Simulated converted ${file.name} to ${targetFormat.toUpperCase()}`], {type: 'application/octet-stream'});
                    resolve(mockBlob);
                }, 2000);
            });
        }

        // [PRODUCTION CONNECTIVITY IMPLEMENTATION]
        // Swaps mock behavior for an active AJAX multi-part payload sent to your edge clusters.
        const formData = new FormData();
        formData.append('file', file);
        formData.append('target', targetFormat);
        formData.append('options', JSON.stringify(options));

        const response = await fetch(this.config.apiEndpoint, {
            method: 'POST',
            body: formData,
            headers: {
                'Accept': 'application/json'
            }
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.message || 'Server conversion failed.');
        }

        return await response.blob();
    }
}

// Global Core UI Bindings
document.addEventListener('DOMContentLoaded', () => {
    // Responsive Navigation Active state toggling
    const mobileToggle = document.getElementById('mobile-toggle') || document.querySelector('.mobile-toggle');
    const navLinks = document.querySelector('.nav-links');

    if (mobileToggle) {
        mobileToggle.addEventListener('click', () => {
            mobileToggle.classList.toggle('active');
            navLinks.classList.toggle('active');
        });
    }

    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            if (mobileToggle) mobileToggle.classList.remove('active');
            if (navLinks) navLinks.classList.remove('active');
        });
    });

    // Accordions handler
    document.querySelectorAll('.accordion-header').forEach(header => {
        header.addEventListener('click', () => {
            header.parentElement.classList.toggle('active');
        });
    });

    // High-performance spotlight hover tracking using event delegation
    document.addEventListener('mousemove', (e) => {
        const card = e.target.closest('.tool-card');
        if (card) {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            card.style.setProperty('--x', `${x}px`);
            card.style.setProperty('--y', `${y}px`);
        }
    });
});

// Expose adapter globally
window.ConversionAdapter = new ConversionEngineAdapter();

// Global developer and utility tool helper functions (Load Sample, Clear, Copy)
window.loadSampleData = () => {
    const input = document.getElementById('dev-input') || document.getElementById('adv-input') || document.getElementById('text-input') || document.getElementById('hash-input') || document.getElementById('qr-data') || document.getElementById('pass-input');
    const input2 = document.getElementById('adv-input-2');
    
    if (!input) return;
    
    const path = window.location.pathname.replace(/\//g, '');
    let sample = "";
    let sample2 = "";
    
    if (path === 'json-to-csv') {
        sample = `[\n  {\n    "id": 1,\n    "name": "Leanne Graham",\n    "username": "Bret",\n    "email": "Sincere@april.biz",\n    "city": "Gwenborough"\n  },\n  {\n    "id": 2,\n    "name": "Ervin Howell",\n    "username": "Antonette",\n    "email": "Shanna@melissa.tv",\n    "city": "Wisokyburgh"\n  }\n]`;
    } else if (path === 'csv-to-json') {
        sample = `id,name,username,email,city\n1,Leanne Graham,Bret,Sincere@april.biz,Gwenborough\n2,Ervin Howell,Antonette,Shanna@melissa.tv,Wisokyburgh`;
    } else if (path === 'base64-tool' || path === 'base64-encode') {
        sample = `freeconvert.cloud is the world's most beautiful, privacy-first SaaS conversion platform. 🚀`;
    } else if (path === 'base64-decode') {
        sample = `ZnJlZWNvbnZlcnQuY2xvdWQgaXMgdGhlIHdvcmxkJ3MgbW9zdCBiZWF1dGlmdWwsIHByaXZhY3ktZmlyc3QgU2FhUyBjb252ZXJzaW9uIHBsYXRmb3JtLiA🚀`;
    } else if (path === 'url-encoder-decoder' || path === 'url-encoder') {
        sample = `https://freeconvert.cloud/search?q=premium saas file converter&secure=true&adsense=safe`;
    } else if (path === 'url-decoder') {
        sample = `https%3A%2F%2Ffreeconvert.cloud%2Fsearch%3Fq%3Dpremium%20saas%20file%20converter%26secure%3Dtrue%26adsense%3Dsafe`;
    } else if (path === 'binary-text-converter') {
        sample = `SaaS File Converter`;
    } else if (path === 'unicode-converter') {
        sample = `Hello World! 🌎 Hello from freeconvert.cloud ⚡`;
    } else if (path === 'sql-formatter') {
        sample = `SELECT u.id, u.name, o.total, o.created_at FROM users u INNER JOIN orders o ON u.id = o.user_id WHERE o.status = 'completed' AND o.total > 150 ORDER BY o.created_at DESC;`;
    } else if (path === 'html-formatter') {
        sample = `<div class="saas-card"><div class="card-header"><h3 class="title">freeconvert.cloud</h3><span class="badge">SaaS</span></div><div class="card-body"><p>Convert files online securely inside your browser local sandbox.</p><a href="/pricing/" class="btn-link">View Plans</a></div></div>`;
    } else if (path === 'css-formatter') {
        sample = `.saas-card { background: rgba(255, 255, 255, 0.75); border: 1px solid rgba(99, 102, 241, 0.08); border-radius: 24px; padding: 2.5rem; transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1); box-shadow: 0 10px 30px rgba(0, 0, 0, 0.02); } .saas-card:hover { transform: translateY(-4px); box-shadow: 0 20px 40px rgba(99, 102, 241, 0.08); }`;
    } else if (path === 'js-formatter' || path === 'javascript-formatter') {
        sample = `const convertFile=async(file,format)=>{const ext=file.name.split('.').pop().toLowerCase();if(window.ConversionAdapter.isClientSideTool(ext,format)){return await window.ConversionAdapter.executeClientSideConversion(file,format)}else{return await window.ConversionAdapter.executeBackendConversion(file,format)}};`;
    } else if (path === 'json-formatter' || path === 'json-validator') {
        sample = `{"id":1,"name":"Leanne Graham","username":"Bret","email":"Sincere@april.biz","address":{"street":"Kulas Light","suite":"Apt. 556","city":"Gwenborough"}}`;
    } else if (path === 'diff-checker') {
        sample = `The quick brown fox jumps over the lazy dog.\nAll conversions run securely.\n100% data privacy.`;
        sample2 = `The fast brown fox jumps over the active dog.\nAll conversions run safely.\n100% client-side privacy.`;
    } else if (path === 'hash-generator') {
        sample = `Secure Sandbox Conversion 🔒`;
    } else if (path === 'word-counter' || path === 'character-counter' || path === 'meta-title-checker' || path === 'meta-description-checker') {
        sample = `freeconvert.cloud is a premium SaaS-level conversion platform. It operates securely inside your local browser memory where possible, guaranteeing maximum privacy and blazing-fast performance. Standard images and text transformations execute offline, ensuring that your records are kept entirely isolated from external servers.`;
    } else if (path === 'case-converter') {
        sample = `the quick brown fox jumps over the lazy dog. convert files online easily.`;
    } else if (path === 'slug-generator') {
        sample = `How to Convert JPG to PDF Online Free in 2026!`;
    } else if (path === 'remove-duplicate-lines') {
        sample = `Leanne Graham\nErvin Howell\nLeanne Graham\nClementine Bauch\nErvin Howell`;
    } else if (path === 'text-cleaner') {
        sample = `<p>  Hello, <b>World</b>!   This is a   messy text blocks.  \n\n\n  Let's clean it up!   </p>`;
    } else if (path === 'qr-generator' || path === 'qr' || path === 'qr-code-generator') {
        sample = `https://freeconvert.cloud/`;
    } else if (path === 'barcode-generator') {
        sample = `freeconvert`;
    } else if (path === 'lorem-ipsum' || path === 'lorem-ipsum-generator') {
        const countInput = document.getElementById('lorem-count');
        if (countInput) countInput.value = 5;
        if (window.generateLorem) window.generateLorem();
        return;
    } else if (path === 'password-strength') {
        sample = `p@$$w0rd_Str0ng_99!`;
    } else if (path === 'image-to-base64') {
        alert('Please choose an image file to convert to Base64.');
        return;
    }
    
    input.value = sample;
    if (input2 && sample2) {
        input2.value = sample2;
    }
    
    input.dispatchEvent(new Event('input'));
};

window.clearInput = () => {
    const input = document.getElementById('dev-input') || document.getElementById('adv-input') || document.getElementById('text-input') || document.getElementById('hash-input') || document.getElementById('qr-data') || document.getElementById('pass-input');
    const input2 = document.getElementById('adv-input-2');
    const output = document.getElementById('dev-output') || document.getElementById('adv-output') || document.getElementById('base64-out') || document.getElementById('lorem-out') || document.getElementById('strength-bar');
    const diffResult = document.getElementById('diff-result-box');
    const qrResult = document.getElementById('qr-result');
    
    if (input) {
        input.value = "";
        input.dispatchEvent(new Event('input'));
    }
    if (input2) {
        input2.value = "";
    }
    if (output) {
        if (output.tagName === 'TEXTAREA' || output.tagName === 'INPUT') {
            output.value = "";
        } else if (output.id === 'strength-bar') {
            const fill = document.getElementById('strength-fill');
            const text = document.getElementById('strength-text');
            if (fill) fill.style.width = '0%';
            if (text) {
                text.textContent = "Enter Password";
                text.style.color = "var(--text-muted)";
            }
        }
    }
    if (diffResult) {
        diffResult.innerHTML = "";
        diffResult.style.display = "none";
    }
    if (qrResult) {
        qrResult.innerHTML = `<span style="color:var(--text-light); font-weight:500;">Your QR Code will render here</span>`;
    }
};

window.copyOutputText = () => {
    const output = document.getElementById('dev-output') || document.getElementById('adv-output') || document.getElementById('base64-out') || document.getElementById('lorem-out') || document.getElementById('password-result') || document.getElementById('hash-input');
    if (!output) return;
    
    let textToCopy = "";
    if (output.tagName === 'SPAN' || output.tagName === 'DIV' || output.tagName === 'CODE') {
        textToCopy = output.textContent;
    } else {
        textToCopy = output.value;
    }
    
    if (!textToCopy || textToCopy.includes('***') || textToCopy === 'Converted results will appear here...' || textToCopy === 'Your QR Code will render here') {
        alert('No converted output to copy yet!');
        return;
    }
    
    navigator.clipboard.writeText(textToCopy).then(() => {
        // Briefly show a success message or alert
        alert('📋 Copied output data securely to clipboard!');
        
        // Trigger delight particles!
        const activeBtn = document.activeElement;
        if (activeBtn) {
            const rect = activeBtn.getBoundingClientRect();
            window.triggerBrandParticles(rect.left + rect.width / 2, rect.top + rect.height / 2);
        }
    }).catch(err => {
        console.error('Clipboard copy failed:', err);
    });
};

/* 🎉 Delight Confetti Particle Burst Trigger */
window.triggerBrandParticles = (x, y) => {
    const colors = ['#6366f1', '#8b5cf6', '#10b981', '#4f46e5', '#7c3aed', '#059669'];
    const particleCount = 28;
    const body = document.body;

    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'delight-particle';
        
        // Randomized color and sizes
        const size = Math.random() * 8 + 6;
        const color = colors[Math.floor(Math.random() * colors.length)];
        
        particle.style.width = size + 'px';
        particle.style.height = size + 'px';
        particle.style.backgroundColor = color;
        particle.style.left = x + 'px';
        particle.style.top = y + 'px';
        
        // Generate random vector angle & travel distance
        const angle = Math.random() * Math.PI * 2;
        const velocity = Math.random() * 120 + 60;
        const tx = Math.cos(angle) * velocity;
        const ty = Math.sin(angle) * velocity;
        
        particle.style.setProperty('--tx', tx + 'px');
        particle.style.setProperty('--ty', ty + 'px');
        
        body.appendChild(particle);
        
        // Clean up DOM after animation completes
        setTimeout(() => {
            particle.remove();
        }, 750);
    }
};

/* 📈 Browser-Local Conversion History Dashboard Tracker */
window.recordConversionHistory = (toolId, toolName, fileName, originalBytes, convertedBytes) => {
    try {
        let history = JSON.parse(localStorage.getItem('freeconvert_history') || '[]');
        let totalFiles = parseInt(localStorage.getItem('freeconvert_total_files') || '0');
        let totalSavings = parseInt(localStorage.getItem('freeconvert_total_savings') || '0');

        // Increment stats
        totalFiles += 1;
        
        let savingsBytes = 0;
        if (originalBytes && convertedBytes && originalBytes > convertedBytes) {
            savingsBytes = originalBytes - convertedBytes;
            totalSavings += savingsBytes;
        }

        // Keep last 15 entries
        const newEntry = {
            id: Date.now() + '_' + Math.random().toString(36).substr(2, 5),
            toolId: toolId,
            toolName: toolName,
            fileName: fileName,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            originalSize: originalBytes,
            convertedSize: convertedBytes,
            savingsBytes: savingsBytes
        };

        history.unshift(newEntry);
        if (history.length > 15) {
            history = history.slice(0, 15);
        }

        localStorage.setItem('freeconvert_history', JSON.stringify(history));
        localStorage.setItem('freeconvert_total_files', totalFiles.toString());
        localStorage.setItem('freeconvert_total_savings', totalSavings.toString());

        // Update dashboard UI dynamically in the DOM
        window.updateDashboardUI();
    } catch (e) {
        console.error("Failed to record conversion history", e);
    }
};

window.updateDashboardUI = () => {
    const filesNumEl = document.getElementById('dash-files-count');
    const savingsEl = document.getElementById('dash-savings-count');
    const historyListEl = document.getElementById('dash-history-list');

    if (!filesNumEl && !historyListEl) return; // Not on page with dashboard

    const totalFiles = localStorage.getItem('freeconvert_total_files') || '0';
    const totalSavingsBytes = parseInt(localStorage.getItem('freeconvert_total_savings') || '0');
    
    // Convert bytes saved to human readable string
    let savingsStr = "0.00 KB";
    if (totalSavingsBytes > 0) {
        if (totalSavingsBytes < 1024 * 1024) {
            savingsStr = (totalSavingsBytes / 1024).toFixed(2) + " KB";
        } else {
            savingsStr = (totalSavingsBytes / 1024 / 1024).toFixed(2) + " MB";
        }
    }

    // Dynamic stats text updates
    if (filesNumEl) filesNumEl.textContent = totalFiles;
    if (savingsEl) savingsEl.textContent = savingsStr;

    if (historyListEl) {
        const history = JSON.parse(localStorage.getItem('freeconvert_history') || '[]');
        if (history.length === 0) {
            historyListEl.innerHTML = `
                <div class="empty-history-state">
                    🌱 Your secure operations log is clean. Start converting files to see metrics in real-time!
                </div>
            `;
        } else {
            historyListEl.innerHTML = history.map(item => {
                let savingsPercentStr = "";
                if (item.savingsBytes > 0 && item.originalSize > 0) {
                    const percent = ((item.savingsBytes / item.originalSize) * 100).toFixed(0);
                    savingsPercentStr = `<span class="savings-badge">-${percent}%</span>`;
                }

                return `
                    <div class="history-card">
                        <div class="history-card-left">
                            <div class="history-card-icon">⚡</div>
                            <div class="history-card-details">
                                <span class="history-file-name" title="${item.fileName}">${item.fileName}</span>
                                <span class="history-file-meta">${item.toolName} • ${item.timestamp}</span>
                            </div>
                        </div>
                        <div class="history-card-right">
                            ${savingsPercentStr}
                            <button class="history-action-btn" title="Open Tool" onclick="location.href='/${item.toolId}/'">➔</button>
                        </div>
                    </div>
                `;
            }).join('');
        }
    }
};

window.resetDashboardStats = () => {
    if (confirm("Are you sure you want to clear your local secure activity log? This cannot be undone.")) {
        localStorage.removeItem('freeconvert_history');
        localStorage.removeItem('freeconvert_total_files');
        localStorage.removeItem('freeconvert_total_savings');
        window.updateDashboardUI();
    }
};

// Initialize Dashboard UI if present
document.addEventListener('DOMContentLoaded', () => {
    window.updateDashboardUI();
});


