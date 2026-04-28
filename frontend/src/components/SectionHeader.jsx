function SectionHeader({ eyebrow, title, subtitle, align = "center" }) {
  const className = `section-header section-header--${align}`;

  return (
    <header className={className}>
      {eyebrow && <p className="section-header-eyebrow">{eyebrow}</p>}
      <h1 className="section-header-title">{title}</h1>
      {subtitle && <p className="section-header-subtitle">{subtitle}</p>}
    </header>
  );
}

export default SectionHeader;
