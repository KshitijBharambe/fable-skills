# Component Architecture

## Purpose

Structure UI components (React-idiom, transferable to Vue/Svelte/Solid) so features stay changeable: right-sized components, state in the right place, composition over configuration, effects kept at the edges.

## When to use

- Building a new feature's component tree.
- A component has grown past ~200 lines or 8 props and changes are getting scary.
- Deciding where a piece of state should live.
- Reviewing frontend PRs for structure (not pixels).
- Designing shared/design-system components others will consume.

## Goals

- Components split by responsibility, not by size or visual region alone.
- State lives at the lowest level that all its readers share.
- Data fetching and side effects at boundaries; the interior is pure render logic.
- Shared components have APIs that survive their fifth consumer without prop explosion.

## Inputs

- The design (all states: loading/empty/error/ideal, all breakpoints).
- Interaction spec: what's clickable, what updates live, what persists.
- Existing component inventory and conventions (naming, file layout, styling approach).
- Data shape from the API and its loading characteristics.

## Outputs

- Component tree sketch with state placement annotated (what state, which component owns it, why).
- Components with typed props, separated concerns, and colocated tests.
- For shared components: a props API designed with the next three consumers in mind, documented with usage examples.

## Expert Mental Model

- **UI is a function of state; components are how you factor that function.** The factoring question is never "how big is this file" but "what changes together, and what varies independently?" Things that change together stay together (colocation); things that vary independently get separated.
- **State placement is the architecture.** Most frontend messes are state living too high (re-render storms, prop drilling, false coupling) or too low (duplicated, out-of-sync copies). The rule: state lives at the lowest common ancestor of everything that reads it — and moves only when a new reader appears.
- **Derive, don't sync.** If a value can be computed from props/state during render, compute it. Copying props into state, or mirroring one state in another via effects, creates two sources of truth that will disagree. `useEffect`-to-synchronize-state is the #1 smell in React codebases.
- **Effects are for escaping the framework, not for program logic.** Subscriptions, DOM measurement, non-React widgets, network in non-framework-managed ways. "When X changes, update Y" belongs in event handlers or derived values, not effects.
- **Composition beats configuration.** A component sprouting `showHeader`, `headerVariant`, `hideFooterOnMobile` booleans is begging to accept `children`/slots instead. Boolean props multiply into untested 2^n states; composition lets each consumer assemble exactly its case.
- **Design shared components like a library author.** Minimal required props, sensible defaults, escape hatches (`className`/style passthrough, render props or slots for the weird cases), and a bias to controlled+uncontrolled support. You can add props forever; removing one is a breaking change.

## Workflow

1. **Enumerate the states before the tree**: loading, empty, error, partial, ideal — per region. Components that ignore non-ideal states get redesigned later under pressure.
2. **Sketch the tree from the design**, drawing boundaries where: (a) a chunk repeats, (b) a chunk owns distinct state, (c) a chunk is a reusable concept, or (d) a chunk can render independently (own loading boundary). Don't split just because a file is long.
3. **Place each piece of state**: list state atoms → for each, find all readers → assign to lowest common ancestor. Mark which are server-cache state (fetched data — belongs in the query layer, not component state), URL state (filters, tabs, selection that should survive refresh/share), or ephemeral UI state (open/closed, drafts).
4. **Identify derived values** and compute them in render (memoize only when measured). Anything you were about to "keep in sync" becomes a computed value or gets a single owner.
5. **Push effects to the edges**: data fetching in route loaders/query hooks at container level; DOM/subscription effects wrapped in custom hooks with tight deps.
6. **Choose controlled vs uncontrolled** for each interactive component: controlled (parent owns value) when siblings/parents need the value live; uncontrolled with `defaultValue` + change callback when they don't. Support `key`-based reset rather than "reset" effects.
7. **Extract custom hooks when logic (not markup) repeats** or when a component's logic paragraph deserves a name (`useUndoableSelection`). Hooks for behavior, components for structure.
8. **Write shared-component APIs against 3 imagined consumers**: current use, the known next use, and one plausible weird one. If the API needs flags to serve them, switch to slots/compound components (`<Select><Select.Trigger/><Select.Options/></Select>`).
9. **Add error boundaries per feature region** and suspense/loading boundaries where the design shows independent loading — boundary placement is a UX decision, not plumbing.
10. **Review pass**: any prop passed through 3+ layers untouched (context or composition candidate), any effect that only sets state from other state (derive it), any boolean prop pair that's really an enum.

## Decision Tree

- If two components need the same state → lift to lowest common ancestor. If that ancestor is far and intermediates don't care → context (for stable/rare-changing values) or an external store slice (for hot values).
- Else if state is fetched from a server → it's cache, not state: query layer (staleness, refetch, dedupe) owns it; components subscribe.
- Else if state should survive refresh or be shareable (filters, pagination, selected tab) → URL, not memory.
- Else → local `useState` in the owning component. Default here; escalate only with a named reason.

When a component feels too big:
- If it renders distinct visual/state regions → split by region with own boundaries.
- Else if markup is one concern but logic is tangled → extract hooks, keep the markup whole.
- Else if it's long but cohesive (a big form) → leave it; length alone isn't debt.

When two components look similar:
- If they share meaning (will always change together) → unify now.
- Else if they merely look alike today → keep both (duplication is cheaper than a wrong abstraction); unify at the third occurrence when the real pattern is visible.

Resetting state when identity changes (new user selected, editing different record):
- Use `key={record.id}` on the subtree — remount is the reset.
- Do not write effects that watch the id and manually null out fields; you will miss one.

## Heuristics

- Props are the component's public API — name them by what they mean to the consumer (`onSelect`, `isDisabled`), not internal mechanics (`setModalFlag`).
- More than ~2 boolean props → look for the hidden enum (`variant="compact" | "full"`) or the composition (`children`).
- A prop drilled through 3 layers untouched is a tunneling smell; a prop *transformed* at each layer is fine — that's the layers doing work.
- List keys: stable identity (ids), never array index when items reorder/insert/delete — index keys cause the classic "input text jumps to the wrong row" bug.
- If a `useEffect` has no cleanup and no external system, interrogate it — most are derived state or event-handler logic in disguise.
- Container/presentational as a hard pattern is dead, but its ghost is right: keep "knows about fetching/stores" components thin and few; keep "renders props" components many and dumb — they're the testable, reusable bulk.
- Colocate aggressively: component + styles + test + story in one folder; a thing you can delete by deleting one folder is a thing with clean boundaries.
- Every callback prop answers "who owns the consequence?" `onDelete(id)` (parent owns) vs deleting internally then `onDeleted()` (child owns) are different architectures — pick per component and stay consistent.
- Render props/slots for "parent decides what to render here"; never `cloneElement` gymnastics.
- Accessibility is structural: interactive things are `<button>`/`<a>`, groups are labeled, focus is managed on mount/unmount of overlays — retrofitting a div-based "button" costs more than using the element did.

## Quality Checklist

- [ ] All five states (loading/empty/error/partial/ideal) rendered per data region.
- [ ] Each state atom has one owner at the lowest common ancestor; no synced copies.
- [ ] No effect exists solely to set state from props/state (derivations computed in render).
- [ ] Server data lives in the query/cache layer; URL-worthy state in the URL.
- [ ] No component >2 boolean display props without a written pass on enum/composition alternatives.
- [ ] List keys are identities.
- [ ] Shared components: required props minimal, escape hatches present, controlled+uncontrolled considered, examples written.
- [ ] Error boundaries around feature regions; loading boundaries match the design's loading UX.
- [ ] `key`-based reset for identity changes.
- [ ] Interactive elements are semantic elements; focus behavior handled in overlays.

## Failure Modes

- **Prop drilling turned context free-for-all**: everything in one giant context → every consumer re-renders on any change. Contexts should be narrow (value changes together) and stable.
- **useEffect state-sync chains**: effect sets A → triggers effect setting B → render storms and impossible-to-trace update loops. Signature: effects whose deps and set-targets are both local state.
- **The God component**: fetching, transforming, and rendering three regions with 14 useStates. Change amplification: every feature touches it, every touch risks the rest.
- **Premature unification**: `Button` and `LinkButton` merged with `as`, `href`, `isExternal`, `variant`, `subtle`… — one component, nine consumers, nobody can change it. The wrong abstraction taxes forever.
- **Copying props to state** (`const [name, setName] = useState(props.name)`) — updates from the parent silently stop applying. If you need "initial value," name it `defaultName` and reset via `key`.
- **Index keys with mutable lists**: deletions shift state (checkboxes, inputs) onto neighboring rows.
- **Modal/overlay state owned globally "for convenience"**: every modal open/close re-renders the app shell.
- **Testing implementation, not contract**: tests full of internal state pokes break on every refactor; test what the user sees and does.

## Edge Cases

- **Stale closures**: callbacks capture old state in long-lived subscriptions/timers — use functional updates (`setX(x => ...)`) or refs for the latest-value pattern.
- **Race conditions on fetch**: user types "ab" then "abc"; "ab" response lands last and wins. Query libraries handle this; hand-rolled fetching needs abort/ignore-stale logic — this bug ships constantly.
- **Hydration mismatches** (SSR): anything reading `window`, `Date.now()`, locale, or random during render differs between server and client — gate behind mount or pass from server.
- **Controlled input cursor jumps**: reformatting value on every keystroke (e.g., currency masks) resets cursor position — format on blur, or manage selection deliberately.
- **Unmount during async**: setState after unmount (warning noise, leaked work) — abort in cleanup; with query layers, mostly free.
- **Layout effects vs effects**: measurement-then-render must use layout effect or the user sees a flicker frame.
- **Portals and event bubbling**: React portals bubble through the React tree, not the DOM tree — click-outside handlers get surprised.
- **Rapid identity switches**: user flips between records faster than fetches resolve — `key` remount + query cancellation handles what manual reset logic never quite does.

## Tradeoffs

- **Colocation vs reuse**: extracting for reuse before a second consumer exists trades today's simplicity for a guess. Duplication is a cheaper mistake than the wrong abstraction — bias to colocate, extract on demonstrated repetition.
- **Fewer big components vs many small**: deep trees of tiny components add indirection (jump through 6 files to find the text); monoliths add change-risk. Optimize for "how many files does the next likely change touch?" — ideally 1–2.
- **Context vs prop passing**: context removes drilling but hides data flow and complicates testing; explicit props are verbose but traceable. Context for app-wide stable values (theme, viewer, i18n); props for feature data.
- **Controlled vs uncontrolled**: controlled gives parents power and costs re-renders + boilerplate; uncontrolled is simpler and faster but opaque. Form libraries exist because "controlled everything" doesn't scale to 40-field forms.
- **Generic design-system component vs product component**: generic components must satisfy unknown consumers (expensive API design); product components can hardcode. Don't build to design-system standards inside one feature.

## Optimization Strategies

- Fix re-render storms by moving state down (into the component that uses it) before reaching for `memo` — state colocation is the performance fix that also improves the architecture.
- `memo` at subtree boundaries where props are stable and subtrees heavy (table rows, chart wrappers); verify with the profiler, not vibes.
- Split contexts by change-frequency: `ViewerContext` (stable) separate from `NotificationsContext` (hot).
- Virtualize long lists (>~200 complex rows); pagination is virtualization you get for free with better UX for business tools.
- Lazy-load below-fold and modal subtrees (`lazy`/dynamic import) — component architecture defines the natural split points.
- Measure with the framework's profiler on a mid-tier device; the fastest render is the component that didn't render.

## Self Review

- For each state atom: who reads it, who writes it, and is it at the lowest common ancestor? Any synced copies anywhere?
- Are there effects I could delete by deriving in render or moving logic into the event handler?
- Which components would I have to touch to: change this feature's layout? add a field? swap the data source? Is each answer ≤2 files?
- Do the non-ideal states exist in code, or only the happy path?
- If a designer asks for "the same thing but slightly different" next sprint, does my shared component absorb it via composition, or do I add prop #11?
- Do my tests survive an internal refactor that preserves behavior?

## Examples

**1. State placement repair.**
Symptom: typing in a search box lags; profiler shows the whole dashboard re-rendering per keystroke. Cause: `searchText` lives in `<DashboardPage>` (top) because the results list needs it. Fix: move `searchText` into `<SearchableList>` (lowest common ancestor of input + results); page-level components no longer re-render. Debounced `onResults` callback informs the page only when selection changes. No `memo` needed — placement was the bug.

**2. Boolean props → composition.**
`<Card title showAvatar avatarUrl showMenu menuItems footerText compact>` — nine props, three consumers, each using a different subset. Redesign to compound components: `<Card><Card.Header avatar={<Avatar/>} action={<Menu/>}>Title</Card.Header><Card.Body/><Card.Footer/></Card>`. Each consumer composes exactly its case; the weird fourth consumer (checkbox in header) needs zero new props. Card's own code shrinks to layout + spacing.

**3. Killing an effect-sync bug.**
Bug: edit form shows the previous user's data after switching rows quickly. Code: `useEffect(() => { setName(user.name); setEmail(user.email); ... }, [user.id])` — misses fields, races fetches. Fix: `<UserEditForm key={user.id} defaultUser={user}/>` — remount on identity change resets everything, including nested state the effect never knew about; the in-flight fetch for the old user is cancelled by the query layer. Effect deleted.

**4. Shared table component that survived.**
Requirement: sortable table for 3 teams. API designed as: `columns: [{id, header, cell: (row) => ReactNode, sortable?}]`, `data`, `onSortChange` (controlled sort — URL owns it), `renderEmpty`, `renderRowActions` slot. Explicit non-goals documented: no built-in fetching, no built-in pagination (compose `<Pagination/>` beside it). Two years later it has 40 consumers and 4 added props — because variation flows through `cell` renderers and slots instead of flags.

## Evaluation Rubric

Score 1–10:

- **1–2**: God components; state placement accidental; effect chains syncing state; index keys; happy-path-only rendering.
- **3–4**: Reasonable visual decomposition but state too high/duplicated; server data in component state; some derived values stored; boolean props accumulating.
- **5–6**: State classified (server/URL/local) and mostly well-placed; derivations computed; effects legitimate; non-ideal states present; shared components workable but flag-heavy.
- **7–8**: Full checklist; composition-first shared APIs; key-based resets; boundaries placed as UX decisions; tests contract-level; re-render behavior verified with profiler.
- **9–10**: Additionally: change-cost consciously minimized (likely changes touch 1–2 files); race/hydration/focus edge cases handled; design-system components with documented API rationale and escape hatches; the tree sketch with state annotations exists and matches reality.
