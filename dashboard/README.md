# Profusion AI Website

Public Vite/React homepage for `profusion.ai`.

## Local Development

```bash
pnpm install
pnpm dev --host 127.0.0.1
```

## Verification

```bash
pnpm lint
pnpm build
```

## Netlify

The repo-level `netlify.toml` deploys this folder as the site base:

- Base directory: `dashboard`
- Build command: `pnpm build`
- Publish directory: `dist`

The contact form uses Netlify Forms. Because the visible form is rendered by React,
`public/__forms.html` contains the static form skeleton Netlify needs at build time.
