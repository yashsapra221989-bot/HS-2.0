import re

with open('public/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract the style block
style_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
if style_match:
    css = style_match.group(1)
    
    # 1. Add grid-bg and scanline classes to CSS
    css = """
    .grid-bg { position: fixed; inset: 0; background-image: linear-gradient(rgba(0,200,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(0,200,255,0.02) 1px, transparent 1px); background-size: 40px 40px; pointer-events: none; z-index: 0; animation: gridDrift 25s linear infinite; }
    @keyframes gridDrift { from { background-position: 0 0; } to { background-position: 40px 40px; } }
    .scanline { position: fixed; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, transparent, var(--accent), transparent); opacity: 0.06; z-index: 1; animation: scanSweep 10s linear infinite; }
    @keyframes scanSweep { from { top: -2px; } to { top: 100vh; } }
    """ + css

    # 2. Update CSS Variables
    css = re.sub(r':root\s*\{.*?\}', '''
    :root {
      --bg: #06080f;
      --surface: #0d1117;
      --surface2: #161b27;
      --surface3: #1e2535;
      --border: #232d42;
      --accent: #00c8ff;
      --green: #00e5a0;
      --red: #ff4757;
      --amber: #ffa94d;
      --text: #e8edf5;
      --text2: #8892a4;
      --text3: #4a5568;
      
      --navy: var(--text);
      --teal: var(--accent);
      --sky: var(--border);
      --beige: var(--bg);
      --white: var(--surface);
      
      --sidebar-w: 220px;
    }
    ''', css, flags=re.DOTALL)

    # 3. Replace color hex codes in CSS to point to our variables
    # Backgrounds
    css = css.replace('#f0f4f8', 'var(--bg)')
    css = css.replace('#f8fafc', 'var(--surface2)')
    css = css.replace('#f1f5f9', 'var(--surface2)')
    css = css.replace('#eef3f7', 'var(--surface3)')
    css = css.replace('#e2eaf0', 'var(--border)')
    css = css.replace('#cbd5e1', 'var(--border)')
    
    # Text colors
    css = css.replace('#94a3b8', 'var(--text2)')
    css = css.replace('#64748b', 'var(--text2)')
    css = css.replace('#475569', 'var(--text)')
    
    # Specific elements
    css = css.replace('background: white;', 'background: var(--surface);')
    css = css.replace('color: white;', 'color: var(--bg);')
    
    # Save the CSS to a file
    with open('public/dashboard.css', 'w', encoding='utf-8') as f:
        f.write(css)
    
    # Remove the style block from HTML and link to CSS
    new_html = content.replace(f'<style>{style_match.group(1)}</style>', '<link rel="stylesheet" href="dashboard.css">')
    
    # 4. Add the animated background layers in HTML
    new_html = new_html.replace('<body>', '<body>\n  <div class="grid-bg"></div>\n  <div class="scanline"></div>')
    
    # 5. Fix any specific inline styles / classes
    new_html = new_html.replace('color: white', 'color: var(--text)')
    
    with open('public/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(new_html)
    
    print("Successfully patched dashboard.html and created dashboard.css")
else:
    print("Could not find style block in dashboard.html")
