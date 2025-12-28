import { Link } from 'react-router-dom';

interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <nav
        style={{
          borderBottom: '1px solid var(--border-subtle)',
          padding: 'clamp(0.75rem, 3vw, 1.5rem)',
          display: 'flex',
          alignItems: 'center',
          gap: 'clamp(0.5rem, 2vw, 1.5rem)',
          flexWrap: 'wrap',
        }}
      >
        <h2 style={{ margin: 0, fontSize: 'clamp(1rem, 2.5vw, 1.25rem)' }}>Deal Hawk</h2>
        <div style={{ display: 'flex', gap: 'var(--space-md)' }}>
          <Link to="/">Overview</Link>
          <Link to="/products">Products</Link>
        </div>
      </nav>
      <main
        style={{
          flex: 1,
          width: '100%',
          padding: 'clamp(1rem, 3vw, 2rem)',
        }}
      >
        {children}
      </main>
    </div>
  );
}

