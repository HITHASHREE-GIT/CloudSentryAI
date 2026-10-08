/**
 * CloudSentry AI — Project Hub
 * One-page launcher for all services.
 */

function Hub() {
  const services = [
    {
      icon: '🛡️',
      title: 'Security Dashboard',
      desc: "CloudSentry AI — View findings for LaunchNest's AWS environment",
      url: 'https://cloudsentry-app.onrender.com',
      badge: 'Live',
    },
    {
      icon: '🏢',
      title: 'Customer SaaS',
      desc: 'LaunchNest — project management platform',
      url: 'https://launchnest-app.onrender.com',
      badge: 'Live',
    },
    {
      icon: '⚙️',
      title: 'Security API',
      desc: 'CloudSentry REST API + Swagger docs',
      url: 'https://cloudsentry-backend.onrender.com/docs',
      badge: 'API',
    },
    {
      icon: '🔐',
      title: 'Customer API',
      desc: 'LaunchNest REST API + Swagger docs',
      url: 'https://launchnest-backend-xtgl.onrender.com/docs',
      badge: 'API',
    },
  ];

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0f1419 0%, #1a2332 100%)',
      color: '#e6edf3',
      padding: '60px 20px',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    }}>
      <div style={{ maxWidth: 1100, margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: 48 }}>
          <h1 style={{
            fontSize: 48,
            background: 'linear-gradient(135deg, #58a6ff 0%, #a78bfa 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            marginBottom: 12,
          }}>
            🛡️ CloudSentry AI
          </h1>
          <p style={{ color: '#8b949e', fontSize: 18 }}>
            Cloud Security Posture Management — Project Hub
          </p>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: 24,
        }}>
          {services.map((s) => (
            <a
              key={s.url}
              href={s.url}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                background: 'rgba(30, 37, 54, 0.6)',
                border: '1px solid #2d3548',
                borderRadius: 16,
                padding: 32,
                textDecoration: 'none',
                color: 'inherit',
                transition: 'all 0.3s',
                display: 'block',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = '#58a6ff';
                e.currentTarget.style.background = 'rgba(88, 166, 255, 0.08)';
                e.currentTarget.style.transform = 'translateY(-4px)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = '#2d3548';
                e.currentTarget.style.background = 'rgba(30, 37, 54, 0.6)';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              <div style={{ fontSize: 48, marginBottom: 16 }}>{s.icon}</div>
              <div style={{
                fontSize: 20,
                fontWeight: 600,
                marginBottom: 8,
                display: 'flex',
                alignItems: 'center',
                gap: 10,
              }}>
                {s.title}
                <span style={{
                  padding: '2px 8px',
                  borderRadius: 4,
                  fontSize: 11,
                  fontWeight: 700,
                  textTransform: 'uppercase',
                  background: 'rgba(88, 166, 255, 0.2)',
                  color: '#58a6ff',
                }}>
                  {s.badge}
                </span>
              </div>
              <div style={{ color: '#8b949e', fontSize: 14, lineHeight: 1.6 }}>
                {s.desc}
              </div>
            </a>
          ))}
        </div>

        <div style={{
          marginTop: 48,
          textAlign: 'center',
          padding: 24,
          background: 'rgba(30, 37, 54, 0.6)',
          border: '1px solid #2d3548',
          borderRadius: 12,
        }}>
          <h3 style={{ color: '#8b949e', fontSize: 14, marginBottom: 12 }}>
            🔑 Demo Login (LaunchNest)
          </h3>
          <code style={{
            background: '#0f1419',
            padding: '8px 16px',
            borderRadius: 6,
            color: '#58a6ff',
            fontFamily: 'Consolas, monospace',
            fontSize: 14,
          }}>
            hira@gmail.com / demo123
          </code>
        </div>

        <div style={{
          marginTop: 40,
          textAlign: 'center',
          color: '#6e7681',
          fontSize: 14,
        }}>
          CloudSentry AI · Built by Hithashree P · T. John Institute of Technology
        </div>
      </div>
    </div>
  );
}

export default Hub;