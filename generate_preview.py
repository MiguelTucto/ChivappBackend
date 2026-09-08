import json
from pathlib import Path

from app.services.email.defaults import EMAIL_TEMPLATE_DEFAULTS
from app.services.email.renderer import render_template

sample_context = {
    "user_name": "Miguel Tucto",
    "user_email": "2cto@chiv.app",
    "musician_name": "Mariachi Los Caballeros",
    "contractor_name": "Carlos Mendoza (Cliente)",
    "member_name": "María Integrante",
    "member_email": "maria.integrante@email.com",
    "leader_name": "Miguel Tucto",
    "app_name": "Chivapp",
    "login_url": "https://chiv.app/login",
    "action_url": "https://chiv.app/musician/bookings/demo-reserva",
    "expires_hours": "48",
    "expires_days": "14",
    "specialties": "Trompeta, Primera Voz, Coro",
    "event_type": "Boda",
    "event_date": "15/08/2026",
    "event_time": "19:00",
    "event_location": "Salón Jardín, Miraflores, Lima",
    "event_description": "Presentación de mariachi de 1 hora para recepción de bodas. Repertorio romántico tradicional.",
}

rendered_templates = {}
for t in EMAIL_TEMPLATE_DEFAULTS:
    slug = t["slug"]
    rendered_templates[slug] = {
        "name": t["name"],
        "description": t["description"],
        "subject": render_template(t["subject"], sample_context),
        "html": render_template(t["html_body"], sample_context),
        "text": render_template(t["text_body"], sample_context),
    }

html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Visor de Correos Chivapp - Brevo</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background: #0B0F19;
      color: #E2E8F0;
      height: 100vh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }}
    header {{
      background: #111827;
      border-bottom: 1px solid #1F2937;
      padding: 14px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    .logo {{
      display: flex;
      align-items: center;
      gap: 10px;
      font-weight: 800;
      font-size: 18px;
      color: #F8FAFC;
    }}
    .badge-brevo {{
      background: #0284C7;
      color: #FFFFFF;
      font-size: 11px;
      font-weight: 700;
      padding: 4px 10px;
      border-radius: 6px;
      letter-spacing: 0.5px;
    }}
    .main-layout {{
      flex: 1;
      display: flex;
      overflow: hidden;
    }}
    .sidebar {{
      width: 320px;
      background: #0F172A;
      border-right: 1px solid #1E293B;
      overflow-y: auto;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}
    .sidebar-title {{
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: #64748B;
      font-weight: 700;
      padding: 6px 12px;
    }}
    .template-btn {{
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      gap: 4px;
      padding: 12px 14px;
      background: #1E293B;
      border: 1px solid #334155;
      border-radius: 10px;
      color: #CBD5E1;
      text-align: left;
      cursor: pointer;
      transition: all 0.15s ease;
      width: 100%;
    }}
    .template-btn:hover {{
      background: #334155;
      color: #FFFFFF;
      border-color: #475569;
    }}
    .template-btn.active {{
      background: #2563EB;
      border-color: #3B82F6;
      color: #FFFFFF;
      box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }}
    .btn-name {{
      font-weight: 700;
      font-size: 14px;
    }}
    .btn-desc {{
      font-size: 12px;
      opacity: 0.8;
      line-height: 1.3;
    }}
    .preview-container {{
      flex: 1;
      display: flex;
      flex-direction: column;
      background: #030712;
      overflow: hidden;
    }}
    .preview-toolbar {{
      background: #111827;
      border-bottom: 1px solid #1F2937;
      padding: 12px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }}
    .subject-bar {{
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 13px;
      color: #94A3B8;
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
    }}
    .subject-value {{
      font-weight: 600;
      color: #F1F5F9;
    }}
    .device-controls {{
      display: flex;
      gap: 8px;
    }}
    .device-btn {{
      background: #1E293B;
      border: 1px solid #334155;
      color: #94A3B8;
      padding: 6px 14px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
    }}
    .device-btn.active {{
      background: #3B82F6;
      border-color: #3B82F6;
      color: #FFFFFF;
    }}
    .viewport {{
      flex: 1;
      display: flex;
      justify-content: center;
      align-items: flex-start;
      padding: 24px;
      overflow-y: auto;
      background: #0A0E17;
    }}
    .frame-wrapper {{
      background: #FFFFFF;
      border-radius: 16px;
      box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.5);
      overflow: hidden;
      transition: width 0.3s ease;
      width: 620px;
      min-height: 700px;
    }}
    .frame-wrapper.mobile {{
      width: 380px;
    }}
    iframe {{
      width: 100%;
      height: 740px;
      border: none;
      display: block;
    }}
  </style>
</head>
<body>
  <header>
    <div class="logo">
      <span>Chivapp</span>
      <span style="color:#64748B;">/</span>
      <span style="font-size: 14px; font-weight: 600; color: #94A3B8;">Visor de Plantillas UI/UX</span>
    </div>
    <div style="display:flex; align-items:center; gap: 12px;">
      <span class="badge-brevo">Proveedor: BREVO (API v3)</span>
    </div>
  </header>

  <div class="main-layout">
    <div class="sidebar">
      <div class="sidebar-title">Plantillas Disponibles</div>
      <div id="buttons-list"></div>
    </div>

    <div class="preview-container">
      <div class="preview-toolbar">
        <div class="subject-bar">
          <span>Asunto:</span>
          <span class="subject-value" id="subject-display"></span>
        </div>
        <div class="device-controls">
          <button class="device-btn active" id="btn-desktop" onclick="setDevice('desktop')">💻 Escritorio</button>
          <button class="device-btn" id="btn-mobile" onclick="setDevice('mobile')">📱 Móvil (380px)</button>
        </div>
      </div>
      <div class="viewport">
        <div class="frame-wrapper" id="frame-wrap">
          <iframe id="preview-frame"></iframe>
        </div>
      </div>
    </div>
  </div>

  <script>
    const templates = {json.dumps(rendered_templates, ensure_ascii=False)};
    let currentSlug = 'booking_member_invite';

    function renderButtons() {{
      const container = document.getElementById('buttons-list');
      container.innerHTML = '';
      for (const [slug, item] of Object.entries(templates)) {{
        const btn = document.createElement('button');
        btn.className = 'template-btn ' + (slug === currentSlug ? 'active' : '');
        btn.onclick = () => selectTemplate(slug);
        btn.innerHTML = `
          <span class="btn-name">${{item.name}}</span>
          <span class="btn-desc">${{item.description}}</span>
        `;
        container.appendChild(btn);
      }}
    }}

    function selectTemplate(slug) {{
      currentSlug = slug;
      renderButtons();
      const item = templates[slug];
      document.getElementById('subject-display').textContent = item.subject;
      const frame = document.getElementById('preview-frame');
      frame.srcdoc = item.html;
    }}

    function setDevice(device) {{
      const wrap = document.getElementById('frame-wrap');
      const bDesk = document.getElementById('btn-desktop');
      const bMob = document.getElementById('btn-mobile');
      if (device === 'mobile') {{
        wrap.classList.add('mobile');
        bMob.classList.add('active');
        bDesk.classList.remove('active');
      }} else {{
        wrap.classList.remove('mobile');
        bDesk.classList.add('active');
        bMob.classList.remove('active');
      }}
    }}

    renderButtons();
    selectTemplate(currentSlug);
  </script>
</body>
</html>
"""

output_path = Path("preview_emails.html")
output_path.write_text(html_content, encoding="utf-8")
print(f"Generado exitosamente en: {output_path.resolve()}")
