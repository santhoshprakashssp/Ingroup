# Global → Region → Tribe Navigation Architecture

## Information Architecture

```
Global Home
├── Global Discovery
│   ├── Region Directory
│   │   ├── Region Overview
│   │   │   ├── Regional Highlights
│   │   │   ├── Featured Tribes
│   │   │   └── Join Region CTA
│   │   ├── Regional Calendar
│   │   └── Regional Resources
│   └── Global Initiatives
├── Search & Filters
│   ├── Keyword Search
│   ├── Filters
│   │   ├── Region
│   │   ├── Tribe Type
│   │   ├── Topic
│   │   └── Membership Status
│   └── Results List
└── Personalized Dashboard (signed-in users)
    ├── My Regions
    ├── My Tribes
    └── Recommended Tribes
```

```
Region Home (per region)
├── Region Hero (description, stats, CTA)
├── Region Navigation Tabs
│   ├── Overview
│   ├── Tribes
│   ├── Events
│   ├── Resources
│   └── Moderation (moderators only)
├── Featured Tribe Highlights
├── Region Activity Feed
└── Membership Panel
    ├── Membership Status Indicator
    ├── Join/Leave Button
    └── Moderator Tools (if applicable)
```

```
Tribe Home (per tribe)
├── Tribe Hero (name, summary, cover, tags)
├── Tribe Navigation Tabs
│   ├── Feed
│   ├── Members
│   ├── Events
│   ├── Resources
│   └── Settings (moderators only)
├── Conversation Feed
├── Upcoming Events Module
├── Resource Library Preview
└── Membership Actions Panel
    ├── Join / Request Access
    ├── Invite Others (members+)
    ├── Report / Flag (members)
    └── Manage Membership (moderators)
```

## Screen & Flow Sketches

### 1. Discovery Flow (Global → Region → Tribe)

```
[Global Landing]
  • Global Highlights
  • Search bar (keyword + filters)
  • Region Directory cards
        ↓ select region
[Region Overview]
  • Region hero + join CTA
  • Tabs: Overview | Tribes | Events | Resources
        ↓ open Tribes tab
[Region Tribes List]
  • Filter: category, size, access level
  • Tribe cards with join status + preview
        ↓ select tribe
[Tribe Landing]
  • Hero (cover, description, tags)
  • Membership panel with primary action (Join / Request / Leave)
  • Feed preview + events + resources
```

### 2. Tribe Landing Page Layout

```
-------------------------------------------------------
| Header: Breadcrumbs (Global > Region > Tribe)       |
|         Tribe name + tag chips                      |
-------------------------------------------------------
| Left column (66%)                                   |
|   - Conversation feed (posts, pinned posts)         |
|   - Upcoming events block                           |
|   - Recent resources                                |
|                                                     |
| Right column (34%)                                  |
|   - Membership status panel                         |
|        • Join / Request / Leave button              |
|        • Member count + roles summary               |
|        • Invite link (members+)                     |
|   - Moderator tools (if moderator)                  |
|   - Region context card                             |
|   - Safety & reporting quick link                   |
-------------------------------------------------------
```

### 3. Membership Actions Flow

```
[Not signed in]
        ↓ CTA → Sign in / Create account
[Signed-in visitor]
        ↓ Click Join
[Permission Check]
  • If open tribe → auto member
  • If approval required → submit request → pending state
  • If invite-only → prompt for invite code
[Member state]
  • Access feed, events, resources, member directory
  • Actions: Leave tribe, Invite others, Report content
[Moderator state]
  • Access member management, content moderation, settings
```

## Roles & Permissions

| Role      | Global Scope                                        | Region Scope                                                         | Tribe Scope                                                                 |
|-----------|------------------------------------------------------|-----------------------------------------------------------------------|------------------------------------------------------------------------------|
| Visitor   | Browse global discovery, search public info.         | View public region overviews and tribe summaries.                     | View public tribe landing (limited), request access if allowed.             |
| Member    | Personalized dashboard, manage profile.              | Join regions, see full region content, RSVP events, access resources. | Join tribes, participate in feed, RSVP events, access resources, invite.    |
| Moderator | Manage global announcements, highlight regions/tribes.| Moderate regional content, approve memberships, manage events/resources.| Moderate tribe content, approve/deny requests, manage roles, edit settings. |

### Permission Nuances by Level

- **Global Moderators** can feature regions/tribes, resolve escalations, and assign regional moderators.
- **Regional Moderators** approve or remove regional members, curate highlighted tribes, and escalate issues to global.
- **Tribe Moderators** manage membership requests, enforce rules, schedule tribe events, and maintain resources.
- **Members** at any level can leave voluntarily and report issues upward.
- **Visitors** must sign in before taking membership actions beyond discovery.
