# 99 Hectare — Frontend Data Dictionary & Roles Guide
> **Audience**: Frontend Developers (React / Next.js / Vue / Mobile)  
> **Scope**: Data Models, Field Specifications, Validation Rules, and Role Responsibilities (User, Agent, Admin).  
> **Notice**: API routes and endpoints are excluded from this document as requested. This serves as the definitive reference for forms, TypeScript interfaces, and UI state management.

---

## 1. Role Responsibilities & Workflows

### 1.1 Regular User (Buyer / Individual Seller)
A standard registered end-user. Roles in backend: `buyer` or `seller`.

* **Profile & Identity**:
  * Registers with full name, email, phone, and password.
  * Manages personal contact info and security settings (password change, OTP verification).
* **Search & Discovery**:
  * Browses and filters property listings (by price range, BHK, locality, furnishing, amenities, etc.).
  * Saves search criteria with notification preferences for new matching listings.
  * Bookmarks / favorites properties for quick access.
* **Direct Interactions (Buyer Flow)**:
  * **Submit Inquiries**: Sends inquiries/leads for properties, projects, agents, or builders. (Users can always view their own unmasked inquiries).
  * **Schedule Visits**: Requests physical or virtual site tours with a preferred date and user notes.
  * **Reviews & Ratings**: Writes 1–5 star ratings and textual comments for agents or builders.
  * **Reports / Complaints**: Flags suspicious listings, fraud agents, or inaccurate prices to platform admins.
* **Individual Seller Flow**:
  * Can list their own single properties directly for Sale or Rent (`owner_id` is automatically attached).
  * Uploads property photos, floor plans, and documents.

---

### 1.2 Agent (Broker / Real Estate Consultant / Agency)
A real estate professional or broker account (`role: agent`).

* **Agent Profile & Trust**:
  * Maintains a professional broker profile: Agency Name, License Number, RERA Registration Number, Experience Years, Profile Photo, and Website.
  * Submits official verification documents to Admin for badge verification (`verification_status`: `PENDING` -> `VERIFIED`).
* **Listings Management**:
  * Creates single property listings or **batch/bulk uploads** multiple property listings at once.
  * Manages property lifecycle: Draft, Active, Sold, Rented.
  * Associates photos, videos, floor plans, brochures, and legal property documents.
* **Leads & Inquiries Gatekeeper Flow (CRITICAL)**:
  * Receives inquiries from prospective buyers who submitted forms on the agent's listings.
  * **Masked Lead Protection**: By platform policy, when a lead arrives, sensitive buyer details (`name`, `email`, `phone`, `message`) are **masked** as `"Lead #<id> (Pending Admin Approval)"` until a platform Admin confirms the lead fee / middle payment.
  * Once Admin approves the inquiry, full buyer contact details are instantly unlocked for the agent to follow up.
* **Site Visits (Tours)**:
  * Receives site visit tour requests from buyers.
  * Can confirm visit slots (`confirmed_date`), add `agent_notes`, or reschedule/cancel with `cancellation_reason`.
* **Public Showcase**:
  * Appears in public agent directories with their verified badge, experience, active listings count, and buyer review ratings.

---

### 1.3 Admin (Platform Moderator / Super Admin)
Platform governing authority (`role: admin`, with level `MODERATOR` or `SUPER_ADMIN`).

* **Platform Governance & User Management**:
  * Views and searches all users across the system.
  * Toggles account activation (`is_active`) and verified statuses (`is_verified`).
* **Property Moderation**:
  * Reviews newly submitted properties before or during publishing.
  * Approves valid listings to make them public (`APPROVED` / `PUBLISHED`).
  * Rejects non-compliant listings with a rejection reason (`PropertyRejectRequest.reason`).
* **Agent & Builder Verification**:
  * Audits uploaded RERA certificates, government licenses, and verification docs.
  * Sets verification status to `VERIFIED`, `REJECTED`, `PENDING`, or `SUSPENDED`.
* **Inquiry Gatekeeper & Middle-Payment Confirmation (Lead Monetization)**:
  * Views all incoming user inquiries platform-wide with unmasked contact info.
  * Serves as the middle gatekeeper: after confirming manual fee/middle payment from the broker, clicks **Approve Inquiry** (optionally attaching `admin_notes`).
  * Can reject fake or abusive inquiries with rejection notes.
* **Complaints & Content Moderation**:
  * Audits user-submitted reports on fake listings, incorrect pricing, or fraudulent agents.
  * Updates report status (`OPEN`, `UNDER_REVIEW`, `RESOLVED`, `REJECTED`) with resolution notes.
* **Audit Trail**:
  * Every administrative moderation action is recorded in `admin_action_logs` (admin ID, action name, entity type, entity ID, description, IP address, timestamp).

---

## 2. Field Specifications by Domain

---

### 2.1 Users & Authentication

#### User Entity (`User`)
| Field Name | Data Type | Required? | Default / Enums | Description / Constraints |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `integer` | Auto (Read-only) | — | Unique user identifier. |
| `full_name` | `string` | **Yes** | — | User's legal full name (1 to 150 chars). |
| `email` | `string` | **Yes** | — | Valid email address, unique in system (max 255 chars). |
| `phone` | `string` | Optional | `null` | Primary mobile number, unique (max 20 chars). |
| `role` | `string` | **Yes** | `"buyer"` | Role: `"buyer"`, `"seller"`, `"agent"`, `"builder"`, `"admin"`. |
| `is_active` | `boolean` | System | `true` | Whether the account is active or suspended. |
| `is_verified` | `boolean` | System | `false` | Email/Phone verified status. |
| `created_at` | `datetime` | Auto (Read-only) | Server now | Account creation timestamp (ISO 8601). |
| `updated_at` | `datetime` | Auto (Read-only) | Server now | Last update timestamp (ISO 8601). |

#### Registration Form Fields (`RegisterRequest`)
| Field Name | Data Type | Required? | Description / UI Guidance |
| :--- | :--- | :--- | :--- |
| `full_name` | `string` | **Yes** | Full name input. |
| `email` | `string` | **Yes** | Valid email input. |
| `phone` | `string` | Optional | Optional mobile number. |
| `password` | `string` | **Yes** | Plain text password. Minimum 6-8 chars. |
| `role` | `string` | Optional | Default `"buyer"`. Can select `"seller"`, `"agent"`, or `"builder"`. |
| `agency_name` | `string` | Optional | Displayed if selected role is `"agent"`. |
| `license_number` | `string` | Optional | Displayed if selected role is `"agent"`. |
| `rera_registration_number` | `string` | Optional | Real estate regulatory license for agents/builders. |
| `experience_years` | `integer` | Optional | Default `0`. Experience in years for agents. |
| `company_name` | `string` | Optional | Displayed if selected role is `"builder"`. |

#### Token & Auth Responses (`TokenResponse`)
| Field Name | Data Type | Description |
| :--- | :--- | :--- |
| `access_token` | `string` | JWT Bearer access token for `Authorization: Bearer <token>`. |
| `refresh_token` | `string` | Token used to renew expired access tokens. |
| `token_type` | `string` | Always `"bearer"`. |
| `role` | `string` | Authenticated user's active role. |
| `user` | `UserResponse` | Complete user object. |

---

### 2.2 Agent Profile (`Agent`)

#### Agent Profile Fields (`AgentResponse` / `AgentCreate` / `AgentUpdate`)
| Field Name | Data Type | Form Input Type | Constraints / Enums | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `integer` | Read-only | — | Unique Agent ID. |
| `user_id` | `integer` | Read-only | — | Linked User account ID. |
| `agency_name` | `string` | Text input | Max 200 chars | Real estate firm or consultancy name. |
| `description` | `string` | Textarea | Optional | Biography, services offered, areas of operation. |
| `license_number` | `string` | Text input | Max 100 chars | Government broker or business license. |
| `experience_years` | `integer` | Number input | `0 <= val <= 100` | Years active in the real estate sector. |
| `profile_image` | `string` | URL / File Upload | Optional | Agent headshot photo URL. |
| `verification_status` | `string` | Badge / Select | `"PENDING"`, `"VERIFIED"`, `"REJECTED"`, `"SUSPENDED"` | Verification state set by Admin. |
| `verification_document` | `string` | URL / File Upload | Optional | Uploaded proof (RERA certificate / ID card). |
| `rera_registration_number`| `string` | Text input | Max 100 chars | Official state RERA license number. |
| `phone` | `string` | Tel input | Max 20 chars | Direct business telephone or mobile. |
| `email` | `string` | Email input | Max 255 chars | Direct business contact email. |
| `website` | `string` | URL input | Valid URL, max 500 | Agency website or portfolio link. |
| `is_featured` | `boolean` | Toggle (Admin) | Default `false` | Promoted banner/top listing agent flag. |
| `is_active` | `boolean` | Toggle | Default `true` | Whether agent profile is currently live. |

---

### 2.3 Admin & Audit Logs (`Admin`, `AdminActionLog`)

#### Admin Entity (`AdminResponse`)
| Field Name | Data Type | Constraints / Enums | Description |
| :--- | :--- | :--- | :--- |
| `id` | `integer` | Read-only | Unique admin profile ID. |
| `user_id` | `integer` | Read-only | Linked User ID. |
| `admin_level` | `string` | `"MODERATOR"`, `"SUPER_ADMIN"` | Permission tier of the admin. |
| `department` | `string` | Max 100 chars, optional | Team (e.g., `"Listing Verification"`, `"Support"`). |
| `is_active` | `boolean` | Default `true` | Admin active status. |
| `last_login_at` | `datetime` | Nullable | Timestamp of previous admin session. |

#### Admin Action Log (`AdminActionResponse`)
| Field Name | Data Type | Description |
| :--- | :--- | :--- |
| `id` | `integer` | Unique action log entry ID. |
| `admin_id` | `integer` | Admin who performed the action. |
| `action` | `string` | Action performed (e.g., `APPROVE_PROPERTY`, `REJECT_PROPERTY`, `VERIFY_AGENT`, `RESOLVE_REPORT`, `APPROVE_INQUIRY`). |
| `entity_type` | `string` | Target resource: `"property"`, `"agent"`, `"builder"`, `"report"`, `"inquiry"`. |
| `entity_id` | `integer` | ID of the affected entity. |
| `description` | `string` | Contextual notes or reason provided by the admin. |
| `ip_address` | `string` | IPv4 or IPv6 address of the admin. |
| `created_at` | `datetime` | Timestamp the moderation action occurred. |

---

### 2.4 Properties (`Property`)

The core entity representing real estate inventory (Apartments, Villas, Plots, Commercial spaces).

#### 2.4.1 Core Property Listing Fields
| Field Name | Data Type | Required? | Constraints / Enums | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `integer` | Read-only | — | Unique property listing ID. |
| `title` | `string` | **Yes** | 5 to 300 chars | Catchy headline (e.g., "Luxury 3 BHK in Sector 62"). |
| `description` | `string` | Optional | Text | Full details, neighborhood highlights, terms. |
| `property_type` | `string` | **Yes** | `"apartment"`, `"villa"`, `"plot"`, `"house"`, `"commercial"`, `"project"` | Classification of real estate. |
| `listing_type` | `string` | **Yes** | `"sell"` (Sale), `"rent"` (Rental), `"lease"` | Transaction category. |
| `status` | `string` | System/Select| `"DRAFT"`, `"PENDING_VERIFICATION"`, `"APPROVED"`, `"REJECTED"`, `"PUBLISHED"`, `"ACTIVE"`, `"SOLD"`, `"RENTED"`, `"EXPIRED"`, `"ARCHIVED"` | Lifecycle status of listing. |
| `is_verified` | `boolean` | System (Admin)| Default `false` | Verified listing badge. |
| `is_featured` | `boolean` | System/Plan | Default `false` | Highlighted on homepage/category top. |
| `is_premium` | `boolean` | System/Plan | Default `false` | Premium tier badge. |
| `is_active` | `boolean` | Toggle | Default `true` | Listing visibility toggle. |

#### 2.4.2 Pricing & Financials
| Field Name | Data Type | Required? | Constraints | Description |
| :--- | :--- | :--- | :--- | :--- |
| `price` | `decimal` | **Yes** | `> 0`, max 15 digits, 2 decimals | Total price (for sale) or monthly rent (for rentals). |
| `price_per_sqft` | `decimal` | Optional | `> 0` | Calculated or specified rate per square foot. |
| `maintenance_charge` | `decimal` | Optional | `>= 0` | Monthly or recurring society maintenance fee. |
| `security_deposit` | `decimal` | Optional | `>= 0` | Security deposit amount (vital for rental properties). |
| `booking_amount` | `decimal` | Optional | `>= 0` | Advance token or booking token amount. |
| `is_price_negotiable` | `boolean` | Optional | Default `false` | Whether owner/broker welcomes negotiations. |

#### 2.4.3 Area & Space Measurements
| Field Name | Data Type | Required? | Constraints | Description |
| :--- | :--- | :--- | :--- | :--- |
| `carpet_area` | `decimal` | Optional | `> 0` | Usable net floor area inside walls. |
| `built_up_area` | `decimal` | Optional | `> 0` | Carpet area + wall thickness + balcony area. |
| `super_built_up_area`| `decimal` | Optional | `> 0` | Built-up area + common shared areas (lobbies, stairs). |
| `plot_area` | `decimal` | Optional | `> 0` | Land/Plot size (crucial for plots and independent villas). |
| `area_unit` | `string` | **Yes** | Default `"SQFT"`. Options: `"SQFT"`, `"SQYD"`, `"SQM"`, `"ACRES"`, `"HECTARE"` | Unit of measurement for area figures. |

#### 2.4.4 Property Specs & Configuration
| Field Name | Data Type | Input Type | Constraints / Enums | Description |
| :--- | :--- | :--- | :--- | :--- |
| `bedrooms` | `integer` | Number / Tabs | `>= 0` (e.g., 1, 2, 3, 4, 5+) | Total bedroom count (BHK). |
| `bathrooms` | `integer` | Number / Tabs | `>= 0` | Number of washrooms. |
| `balconies` | `integer` | Number / Tabs | `>= 0` | Balcony count. |
| `floor_number` | `integer` | Number | Can be negative for basement | Floor on which unit is located. |
| `total_floors` | `integer` | Number | `>= 0` | Total floors in the building/tower. |
| `furnishing_status` | `string` | Dropdown | `"unfurnished"`, `"semi-furnished"`, `"fully-furnished"` | Furnishing state. |
| `facing` | `string` | Dropdown | `"North"`, `"South"`, `"East"`, `"West"`, `"North-East"`, `"North-West"`, `"South-East"`, `"South-West"` | Vastu / Directional orientation. |
| `parking_spaces` | `integer` | Number | `>= 0` | Reserved car parking spots. |
| `property_age` | `integer` | Number | `>= 0` (in years) | Age of the property structure. |
| `year_built` | `integer` | Year picker | Range `1800` to `2100` | Construction completion year. |
| `construction_status`| `string` | Dropdown | `"ready_to_move"`, `"under_construction"` | Delivery status. |
| `possession_date` | `date` | Date picker | Format: `YYYY-MM-DD` | Target or actual handover date. |

#### 2.4.5 Location & Mapping
| Field Name | Data Type | Required? | Description |
| :--- | :--- | :--- | :--- |
| `country_id` | `integer` | Optional | Country reference ID. |
| `state_id` | `integer` | Optional | State reference ID. |
| `city_id` | `integer` | Optional | City reference ID. |
| `locality_id` | `integer` | Optional | Locality / Sector reference ID. |
| `sub_locality_id` | `integer` | Optional | Sub-locality / Pocket / Block ID. |
| `address` | `string` | Optional | Full street address or society name. |
| `landmark` | `string` | Optional | Prominent nearby landmark (max 250 chars). |
| `pincode` | `string` | Optional | Postal code (max 20 chars). |
| `latitude` | `float` | Optional | GPS Latitude (`-90.0` to `90.0`). |
| `longitude` | `float` | Optional | GPS Longitude (`-180.0` to `180.0`). |

#### 2.4.6 Ownership, Legal & Relations
| Field Name | Data Type | Required? | Description |
| :--- | :--- | :--- | :--- |
| `owner_id` | `integer` | Optional | ID of the User who owns the property. |
| `agent_id` | `integer` | Optional | ID of the Agent marketing the property. |
| `builder_id` | `integer` | Optional | ID of the Builder firm developing the property. |
| `project_id` | `integer` | Optional | ID of the Project township/society this unit belongs to. |
| `rera_number` | `string` | Optional | State RERA registration ID for this listing (max 150 chars). |
| `ownership_type` | `string` | Optional | E.g., `"Freehold"`, `"Leasehold"`, `"Power of Attorney"`, `"Co-operative Society"`. |
| `amenity_ids` | `list[int]` | Optional | Array of Amenity IDs associated with this property. |

---

### 2.5 Specific Sub-Property Details

When rendering or creating a specific property type, additional dedicated detail objects are used:

#### 2.5.1 Residential Details (`ResidentialPropertyDetails`)
*Only applicable for Apartments, Villas, and Houses.*

| Field Name | Data Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `servant_room` | `boolean` | `false` | Dedicated domestic help room. |
| `study_room` | `boolean` | `false` | Study or home office room. |
| `pooja_room` | `boolean` | `false` | Dedicated prayer room. |
| `store_room` | `boolean` | `false` | Dedicated utility/storage room. |
| `other_room` | `string` | `null` | Any other room description (max 100 chars). |
| `electricity_available`| `boolean`| `true` | Reliable electrical supply connection. |
| `water_supply` | `string` | `null` | Water source: `"Corporation"`, `"Borewell"`, `"Both"`. |
| `gas_pipeline` | `boolean` | `false` | Piped natural gas (PNG) connection. |

#### 2.5.2 Commercial Details (`CommercialPropertyDetails`)
*Only applicable for Commercial Offices, Shops, and Showrooms.*

| Field Name | Data Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `commercial_sub_type`| `string` | `null` | E.g., `"Office"`, `"Retail Shop"`, `"Showroom"`, `"Warehouse"`. |
| `washrooms` | `integer` | `null` | Count of private/common washrooms. |
| `conference_rooms` | `integer` | `null` | Dedicated meeting rooms. |
| `cabins` | `integer` | `null` | Executive or team cabins. |
| `pantry` | `boolean` | `false` | Dry or wet pantry availability. |
| `reception_area` | `boolean` | `false` | Dedicated reception/waiting lounge. |
| `power_backup` | `boolean` | `false` | 100% DG power backup availability. |

#### 2.5.3 Plot Details (`PlotPropertyDetails`)
*Only applicable for Residential Plots, Commercial Land, and Agricultural Parcels.*

| Field Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `plot_length` | `decimal` | `> 0` | Length of plot in feet/meters. |
| `plot_width` | `decimal` | `> 0` | Breadth/width of plot in feet/meters. |
| `road_width` | `decimal` | `> 0` | Width of facing road in front of the plot. |
| `boundary_wall` | `boolean` | Default `false` | Whether boundary perimeter wall is built. |
| `corner_plot` | `boolean` | Default `false` | Whether plot has two or more open road sides. |
| `gated_community`| `boolean` | Default `false` | Located within a secured gated layout. |

---

### 2.6 Media & Documents

#### Property Media (`PropertyMediaResponse` / `PropertyMediaCreateInput`)
| Field Name | Data Type | Required? | Constraints / Enums | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `integer` | Read-only | — | Unique media ID. |
| `property_id` | `integer` | **Yes** | — | Associated property. |
| `media_type` | `string` | **Yes** | `"IMAGE"`, `"VIDEO"`, `"FLOOR_PLAN"`, `"BROCHURE"`, `"VIRTUAL_TOUR"` | Asset classification. |
| `url` | `string` | **Yes** | Valid URL | Direct link to high-resolution asset (Cloudinary/S3). |
| `thumbnail_url` | `string` | Optional | Valid URL | Compressed preview thumbnail URL. |
| `title` | `string` | Optional | Max 200 chars | Caption (e.g., "Master Bedroom Balcony View"). |
| `sort_order` | `integer` | Optional | Default `0`, `>= 0` | Order in which media appears in gallery carousel. |
| `is_primary` | `boolean` | Optional | Default `false` | **Hero Image**: If `true`, used as the primary card cover thumbnail. |

#### Property Legal Documents (`PropertyDocumentResponse`)
| Field Name | Data Type | Enums / Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `integer` | Read-only | Unique document ID. |
| `property_id` | `integer` | Required | Target property. |
| `document_type` | `string` | E.g., `"title_deed"`, `"rera_certificate"`, `"occupancy_certificate"`, `"tax_receipt"` | Category of legal certificate. |
| `document_url` | `string` | Valid URL | PDF or image link. |
| `verification_status`| `string` | `"PENDING"`, `"VERIFIED"`, `"REJECTED"` | Admin approval status of document. |
| `remarks` | `string` | Optional text | Admin review notes or rejection feedback. |

---

### 2.7 Inquiries & Lead Monetization Gatekeeper

This domain controls contact requests from prospective buyers to agents or builders.

#### Inquiry Fields (`InquiryResponse` / `InquiryCreate`)
| Field Name | Data Type | Required? | Constraints / Enums | Description & Frontend Masking Behavior |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `integer` | Read-only | — | Unique inquiry / lead ID. |
| `user_id` | `integer` | Auto | — | ID of the buyer who submitted the form. |
| `property_id` | `integer` | Optional | — | ID of property inquired about. |
| `project_id` | `integer` | Optional | — | ID of project inquired about. |
| `agent_id` | `integer` | Optional | — | Target agent. |
| `builder_id` | `integer` | Optional | — | Target builder. |
| `name` | `string` | Optional | Max 150 chars | **Masked for Agents until Admin approves**: Shows `"Lead #<id> (Pending Admin Approval)"` until confirmed. Full name when approved. |
| `email` | `string` | Optional | EmailStr | **Masked**: Returns `null` to Agent until `is_admin_approved == true`. |
| `phone` | `string` | Optional | Max 20 chars | **Masked**: Returns `null` to Agent until `is_admin_approved == true`. |
| `message` | `string` | Optional | Text | **Masked**: Masked warning message returned to Agent until `is_admin_approved == true`. |
| `status` | `string` | Optional | `"NEW"`, `"CONTACTED"`, `"INTERESTED"`, `"VISITED"`, `"CONVERTED"`, `"CLOSED"`, `"CANCELLED"`, `"APPROVED"`, `"REJECTED"`, `"PENDING_APPROVAL"` | Lead management status for CRM tracking. |
| `source` | `string` | Optional | E.g., `"website"`, `"mobile_app"`, `"call"` | Origin channel of lead. |
| `is_admin_approved` | `boolean` | Admin-only | Default `false` | **Gatekeeper flag**: When `true`, lead contact details unlock for agent/owner. |
| `admin_notes` | `string` | Admin-only | Text | Notes by admin regarding payment confirmation. |

---

### 2.8 Site Visits & Tours (`Visit`)

Allows buyers to book in-person or virtual property tours with an agent.

#### Visit Fields (`VisitResponse` / `VisitCreate` / `VisitStatusUpdate`)
| Field Name | Data Type | Input / Source | Constraints / Enums | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `integer` | Read-only | — | Unique visit booking ID. |
| `user_id` | `integer` | Read-only | — | Buyer who requested the tour. |
| `property_id` | `integer` | **Yes** | — | Property to be visited. |
| `agent_id` | `integer` | Optional | — | Agent assigned to host the tour. |
| `requested_date` | `datetime` | **Yes** | ISO 8601 | Buyer's preferred visit time slot. |
| `confirmed_date` | `datetime` | Agent/Admin | ISO 8601, nullable | Confirmed scheduled slot by the agent. |
| `status` | `string` | Select | `"REQUESTED"`, `"CONFIRMED"`, `"COMPLETED"`, `"CANCELLED"`, `"RESCHEDULED"` | Tour booking progress status. |
| `user_notes` | `string` | Textarea | Optional | Buyer's special requirements (e.g., "Will come with architect"). |
| `agent_notes` | `string` | Textarea | Optional (Agent/Admin) | Agent's internal log or feedback after visit. |
| `cancellation_reason`| `string`| Textarea | Optional | Reason provided if visit is declined or cancelled. |

---

### 2.9 Reviews & Ratings (`Review`)

Social proof and credibility ratings left by buyers for agents and builders.

#### Review Fields (`ReviewResponse` / `ReviewCreate`)
| Field Name | Data Type | Required? | Constraints | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `integer` | Read-only | — | Unique review ID. |
| `user_id` | `integer` | Read-only | — | Buyer author ID. |
| `agent_id` | `integer` | Optional | — | Target agent being reviewed (if applicable). |
| `builder_id` | `integer` | Optional | — | Target builder being reviewed (if applicable). |
| `rating` | `integer` | **Yes** | `1 <= rating <= 5` | Star rating (1 to 5 whole stars). |
| `comment` | `string` | Optional | Max 2000 chars | Detailed written testimonial or review. |
| `is_verified` | `boolean` | Admin | Default `false` | Verified buyer badge (confirmed transaction). |
| `is_published` | `boolean` | Admin/Toggle | Default `true` | Public visibility flag. |

---

### 2.10 Reports & Complaints (`Report`)

User reporting mechanism to flag fraudulent listings, incorrect info, or abusive agents.

#### Report Fields (`ReportResponse` / `ReportCreate` / `ReportUpdate`)
| Field Name | Data Type | Required? | Constraints / Enums | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `integer` | Read-only | — | Unique report ID. |
| `reporter_id` | `integer` | Read-only | — | User who submitted the complaint. |
| `property_id` | `integer` | Optional | — | Target property flagged. |
| `agent_id` | `integer` | Optional | — | Target agent flagged. |
| `builder_id` | `integer` | Optional | — | Target builder flagged. |
| `reported_user_id` | `integer` | Optional | — | Target user flagged. |
| `reason` | `string` | **Yes** | 2 to 100 chars (e.g., `"FAKE_LISTING"`, `"WRONG_PRICE"`, `"SOLD_ALREADY"`, `"FRAUD"`) | Predefined or short complaint reason. |
| `description` | `string` | Optional | Text | Detailed explanation of the issue. |
| `status` | `string` | Admin | `"OPEN"`, `"UNDER_REVIEW"`, `"RESOLVED"`, `"REJECTED"` | Moderation ticket status. |
| `admin_notes` | `string` | Admin | Text, nullable | Internal notes on how the issue was addressed. |
| `resolved_by` | `integer` | Admin | Nullable | Admin ID who resolved the report. |
| `resolved_at` | `datetime` | Admin | Nullable | Timestamp of resolution. |

---

### 2.11 Subscriptions & Monetization Plans

#### Subscription Plan (`SubscriptionPlanResponse`)
| Field Name | Data Type | Description |
| :--- | :--- | :--- |
| `id` | `integer` | Plan ID. |
| `name` | `string` | Plan title (e.g., `"Silver Agent"`, `"Gold Broker"`, `"Builder Pro"`). |
| `description` | `string` | Marketing description of benefits. |
| `price` | `float / decimal` | Plan fee (in INR). |
| `duration_days` | `integer` | Plan validity period in days (e.g. 30, 90, 365). |
| `max_listings` | `integer` | Number of active properties allowed to be listed. |
| `max_inquiries` | `integer` | Quota of unmasked leads allowed. |
| `max_saved_searches`| `integer` | Number of alert searches allowed. |
| `featured_listing_allowed`| `boolean` | Allows user/agent to feature listings on top slots. |
| `priority_support`| `boolean` | Priority customer care badge. |
| `is_active` | `boolean` | Whether plan is currently available for purchase. |

#### User Subscription Active Status (`UserSubscriptionResponse`)
| Field Name | Data Type | Description |
| :--- | :--- | :--- |
| `id` | `integer` | Active subscription record ID. |
| `user_id` | `integer` | Subscribing user/agent. |
| `plan_id` | `integer` | Target plan ID. |
| `start_date` | `datetime` | Validity start timestamp. |
| `end_date` | `datetime` | Expiry timestamp. |
| `status` | `string` | `"ACTIVE"`, `"EXPIRED"`, `"CANCELLED"`. |
| `auto_renew` | `boolean` | Auto renewal toggle. |
| `remaining_inquiries`| `integer` | Remaining lead unlocks in current billing cycle. |
| `remaining_listings` | `integer` | Remaining properties user can publish. |

---

### 2.12 Payments & Transactions (`Payment`)

#### Payment Fields (`Payment`)
| Field Name | Data Type | Constraints / Enums | Description |
| :--- | :--- | :--- | :--- |
| `id` | `integer` | Read-only | Unique transaction ID. |
| `user_id` | `integer` | Required | Payer user ID. |
| `subscription_id` | `integer` | Optional | Linked subscription plan (if paying for subscription). |
| `amount` | `decimal` | Required, 2 decimals | Billed transaction amount. |
| `currency` | `string` | Default `"INR"` | Currency ISO code. |
| `payment_gateway` | `string` | E.g., `"RAZORPAY"`, `"STRIPE"` | Payment provider name. |
| `gateway_payment_id`| `string`| Nullable | Transaction reference ID from payment gateway. |
| `gateway_order_id` | `string` | Nullable | Order reference ID from payment gateway. |
| `status` | `string` | `"PENDING"`, `"SUCCESS"`, `"FAILED"`, `"REFUNDED"` | Transaction state. |
| `payment_method` | `string` | Nullable (e.g., `"UPI"`, `"CREDIT_CARD"`, `"NETBANKING"`) | Payment method used. |
| `payment_metadata` | `object / json` | Nullable | Raw metadata/webhook payload from gateway. |

---

### 2.13 Saved Searches & Favorites

#### Saved Search (`SavedSearchResponse` / `SavedSearchCreate`)
| Field Name | Data Type | Required? | Constraints | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `integer` | Read-only | — | Unique saved search ID. |
| `name` | `string` | **Yes** | 2 to 200 chars | Name given by user (e.g., "3 BHK under 1.5 Cr in Noida"). |
| `city_id` | `integer` | Optional | — | Targeted city. |
| `locality_id` | `integer` | Optional | — | Targeted locality. |
| `property_type` | `string` | Optional | Max 50 chars | Target property type. |
| `listing_type` | `string` | Optional | Max 30 chars | `"sell"`, `"rent"`, etc. |
| `min_price` / `max_price` | `decimal` | Optional | `>= 0` | Budget range filter. |
| `min_area` / `max_area` | `decimal` | Optional | `>= 0` | Area range filter. |
| `bedrooms` | `integer` | Optional | `>= 0` | BHK filter. |
| `furnishing_status` | `string` | Optional | Dropdown | Furnishing filter. |
| `filters` | `object / json` | Optional | JSON key-values | Arbitrary additional search filters. |
| `notify_new_listings`| `boolean`| Optional | Default `false` | **Alert toggle**: Sends notifications when new matching properties appear. |
| `is_active` | `boolean` | Optional | Default `true` | Search alert active status. |

#### Favorite (`FavoriteResponse` / `FavoriteCreate`)
| Field Name | Data Type | Required? | Description |
| :--- | :--- | :--- | :--- |
| `id` | `integer` | Read-only | Unique favorite ID. |
| `user_id` | `integer` | Auto | Current user ID. |
| `property_id` | `integer` | **Yes** | Property bookmarked by the user. |
| `created_at` | `datetime` | Auto | Bookmark timestamp. |

---

### 2.14 In-App Notifications (`Notification`)

| Field Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `integer` | Read-only | Notification record ID. |
| `user_id` | `integer` | Required | Recipient user ID. |
| `title` | `string` | Max 200 chars | Notification header (e.g. "Visit Confirmed", "Lead Approved"). |
| `message` | `string` | Text | Body content of the notification. |
| `notification_type`| `string` | Max 50 chars | Category: `"VISIT"`, `"INQUIRY"`, `"PROPERTY"`, `"SYSTEM"`. |
| `is_read` | `boolean` | Default `false` | Unread badge toggle. Marked `true` when user clicks it. |
| `action_url` | `string` | Nullable | Deep link or frontend route to redirect user upon clicking. |
| `created_at` | `datetime` | Read-only | Creation timestamp. |

---

### 2.15 Locations Hierarchy

Hierarchical geographic datasets used for cascaded location dropdowns in search and property posting forms:

```
Country
  └── State
        └── City
              └── Locality (Sector / Area)
                    └── SubLocality (Pocket / Block / Phase)
```

| Entity | Fields | Description |
| :--- | :--- | :--- |
| **Country** | `id`, `name`, `iso_code`, `phone_code` | National boundary (e.g., India, `IN`, `+91`). |
| **State** | `id`, `country_id`, `name`, `state_code` | State or province (e.g., Uttar Pradesh, `UP`). |
| **City** | `id`, `state_id`, `name`, `latitude`, `longitude` | City or district (e.g., Noida, Delhi, Mumbai). |
| **Locality** | `id`, `city_id`, `name`, `pincode`, `latitude`, `longitude` | Sector or neighborhood (e.g., "Sector 62", "Indirapuram"). |
| **SubLocality**| `id`, `locality_id`, `name`, `pincode`, `latitude`, `longitude` | Specific pocket, block, or sub-division. |

---

### 2.16 Amenities (`Amenity`)

Checklist features associated with properties or builder projects (e.g., Swimming Pool, 24/7 Security, Gymnasium).

| Field Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `integer` | Read-only | Unique amenity ID. |
| `name` | `string` | Unique, max 100 chars | Name (e.g., `"Swimming Pool"`, `"Clubhouse"`, `"Power Backup"`). |
| `category` | `string` | Max 100 chars | Grouping: `"Sports"`, `"Safety & Security"`, `"Convenience"`, `"Eco-friendly"`. |
| `description`| `string` | Optional text | Detailed description of amenity. |
| `icon` | `string` | Max 500 chars | Lucide/Material icon name or SVG/image URL. |
| `is_active` | `boolean` | Default `true` | Visibility toggle in filter lists. |

---

### 2.17 Builders & Projects (Reference)

For builder firm profiles and new development projects:

* **Builder Profile (`Builder`)**:
  * `company_name`: string (required, max 200)
  * `description`: text
  * `website`, `email`, `phone`, `logo` (URL)
  * `license_number`, `rera_registration_number`
  * `verification_status`: `"PENDING"`, `"VERIFIED"`, `"REJECTED"`
  * `verification_document`: string (URL)
  * `established_year`: integer
  * `is_featured`, `is_active`: boolean
* **Project (`Project`)**:
  * `name`: string (required, max 250)
  * `builder_id`: integer (required)
  * `project_type`: string (`"residential"`, `"commercial"`, `"township"`)
  * `status`: string (`"upcoming"`, `"under_construction"`, `"ready_to_move"`, `"completed"`)
  * `price_from`, `price_to`: decimal
  * `total_units`, `total_towers`: integer
  * `possession_date`: date (`YYYY-MM-DD`)
  * Location fields: `country_id`, `state_id`, `city_id`, `locality_id`, `address`, `landmark`, `pincode`, `latitude`, `longitude`, `rera_number`
* **Project Unit (`ProjectUnit`)**:
  * `name`: string (e.g., "3 BHK Luxury Suite")
  * `configuration`: string (e.g., "3BHK+3T")
  * `bedrooms`, `bathrooms`: integer
  * `area`: decimal, `area_unit`: string (default `"SQFT"`)
  * `price_from`, `price_to`: decimal
  * `total_units`, `available_units`: integer

---

## 3. Key Frontend Logic & UI States Summary

1. **Inquiry Masking (Buyer Lead Protection)**:
   * On Agent / Owner Lead screens: If `is_admin_approved == false`, display a banner or locked lock icon: `"Contact details locked. Admin verification / payment pending."`
   * Only render the phone call button, email button, and buyer name when `is_admin_approved == true`.
2. **Property Form Cascading**:
   * Choosing `property_type == "apartment" | "villa" | "house"` renders the **Residential Details** section (servant room, pooja room, water supply, gas pipeline).
   * Choosing `property_type == "commercial"` renders the **Commercial Details** section (cabins, washrooms, conference rooms, pantry, power backup).
   * Choosing `property_type == "plot"` renders the **Plot Details** section (plot dimensions, road width, boundary wall, corner plot).
3. **Role-Based Navigation**:
   * **Buyer / Seller**: Profile, My Favorites, My Saved Searches, My Inquiries, My Visits, Post Property (Individual Owner).
   * **Agent**: Agent Profile & Verification, My Listings, Bulk Property Upload, My Leads / Inquiries (Received), Visit Requests Calendar, Reviews.
   * **Admin**: Admin Dashboard, User Directory, Property Approval Queue, Agent Verification Requests, Lead Gatekeeper (Approve/Reject Inquiries), Complaint Resolution, System Action Logs.
