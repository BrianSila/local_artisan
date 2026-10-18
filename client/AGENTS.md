<!-- LOVABLE:BEGIN -->
> [!IMPORTANT]
> This project is connected to [Lovable](https://lovable.dev). Avoid rewriting
> published git history — force pushing, or rebasing/amending/squashing commits
> that are already pushed — as it rewrites history on Lovable's side and the
> user will likely lose their project history.
>
> Commits you push to the connected branch sync back to Lovable and show up in
> the editor, so keep the branch in a working state.
<!-- LOVABLE:END -->

- Keep all remote business operations in the typed browser API client under src/lib/local; the existing Flask API owns authentication and authorization, so never substitute another backend.
- Store the Flask session in sessionStorage and gate private screens with the client-only _account layout; server endpoint permission checks remain authoritative.
- Clear query caches on session loss, not initial signed-out hydration; clearing during public query startup leaves live marketplace reads cancelled.
- Keep reusable marketplace screens under src/components/local and thin file-based routes under src/routes; shared site chrome belongs in the root layout.
- Define all visual tokens and reusable screen styles in src/styles.css so marketplace and account pages share one design system.
