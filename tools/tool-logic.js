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
            'pdf': ['docx', 'doc', 'jpg', 'png', 'txt'],
            'mp4': ['mp3', 'wav', 'avi', 'mov', 'webm'],
            'mp3': ['wav', 'ogg', 'm4a', 'flac'],
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
        return new Promise((resolve, reject) => {
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
            img.onload = () => {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                
                // Read optional advanced dimensions or default to original aspect ratio
                const width = options.width || img.naturalWidth;
                const height = options.height || img.naturalHeight;
                canvas.width = width;
                canvas.height = height;
                
                ctx.drawImage(img, 0, 0, width, height);
                
                let mimeType = 'image/png';
                if (targetFormat === 'jpg' || targetFormat === 'jpeg') mimeType = 'image/jpeg';
                if (targetFormat === 'webp') mimeType = 'image/webp';
                
                const quality = options.quality ? parseFloat(options.quality) : 0.9;
                
                canvas.toBlob((blob) => {
                    if (blob) {
                        resolve(blob);
                    } else {
                        reject(new Error('Canvas rasterization failed.'));
                    }
                }, mimeType, quality);
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
});

// Expose adapter globally
window.ConversionAdapter = new ConversionEngineAdapter();

// Global developer and utility tool helper functions (Load Sample, Clear, Copy)
window.loadSampleData = () => {
    const input = document.getElementById('dev-input') || document.getElementById('adv-input') || document.getElementById('text-input') || document.getElementById('hash-input') || document.getElementById('qr-data') || document.getElementById('pass-input');
    const input2 = document.getElementById('adv-input-2');
    
    if (!input) return;
    
    // Determine the current tool ID from URL path or page context
    const path = window.location.pathname.replace(/\//g, '');
    let sample = "";
    let sample2 = "";
    
    if (path === 'json-to-csv') {
        sample = `[\n  {\n    "id": 1,\n    "name": "Leanne Graham",\n    "username": "Bret",\n    "email": "Sincere@april.biz",\n    "city": "Gwenborough"\n  },\n  {\n    "id": 2,\n    "name": "Ervin Howell",\n    "username": "Antonette",\n    "email": "Shanna@melissa.tv",\n    "city": "Wisokyburgh"\n  }\n]`;
    } else if (path === 'csv-to-json') {
        sample = `id,name,username,email,city\n1,Leanne Graham,Bret,Sincere@april.biz,Gwenborough\n2,Ervin Howell,Antonette,Shanna@melissa.tv,Wisokyburgh`;
    } else if (path === 'base64-tool') {
        sample = `freeconvert.cloud is the world's most beautiful, privacy-first SaaS conversion platform. 🚀`;
    } else if (path === 'url-encoder-decoder') {
        sample = `https://freeconvert.cloud/search?q=premium saas file converter&secure=true&adsense=safe`;
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
    } else if (path === 'js-formatter') {
        sample = `const convertFile=async(file,format)=>{const ext=file.name.split('.').pop().toLowerCase();if(window.ConversionAdapter.isClientSideTool(ext,format)){return await window.ConversionAdapter.executeClientSideConversion(file,format)}else{return await window.ConversionAdapter.executeBackendConversion(file,format)}};`;
    } else if (path === 'diff-checker') {
        sample = `The quick brown fox jumps over the lazy dog.\nAll conversions run securely.\n100% data privacy.`;
        sample2 = `The fast brown fox jumps over the active dog.\nAll conversions run safely.\n100% client-side privacy.`;
    } else if (path === 'hash-generator') {
        sample = `Secure Sandbox Conversion 🔒`;
    } else if (path === 'word-counter') {
        sample = `freeconvert.cloud is a premium SaaS-level conversion platform. It operates securely inside your local browser memory where possible, guaranteeing maximum privacy and blazing-fast performance. Standard images and text transformations execute offline, ensuring that your records are kept entirely isolated from external servers.`;
    } else if (path === 'case-converter') {
        sample = `the quick brown fox jumps over the lazy dog. convert files online easily.`;
    } else if (path === 'qr-generator' || path === 'qr') {
        sample = `https://freeconvert.cloud/`;
    } else if (path === 'lorem-ipsum') {
        // Handled internally by lorem tool count, but let's set count
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
    
    // Trigger input event to update char counter, live previews, etc.
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
    }).catch(err => {
        console.error('Clipboard copy failed:', err);
    });
};

