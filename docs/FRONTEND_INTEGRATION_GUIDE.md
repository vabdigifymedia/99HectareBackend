# 99 Hectares Backend — Frontend Integration & API Documentation

This guide provides a comprehensive integration manual for frontend developers connecting web, mobile, or admin dashboards to the **99 Hectares Real Estate Backend API**.

---

## 1. Quick Start & Server Environment

### Base URLs
- **Local API Base URL**: `http://localhost:8000/api/v1`
- **Interactive Swagger UI**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`
- **System Health Diagnostics**: `GET http://localhost:8000/api/v1/system/status`

### Pre-Seeded Demo Accounts for Development & QA
| Role | Email | Password | Purpose |
| :--- | :--- | :--- | :--- |
| **Buyer / User** | `aditya.mehta@example.com` | `password123` | Search, favorite properties, submit inquiries, schedule site visits |
| **Agent / Dealer** | `vikram.sharma@horizonrealty.in` | `password123` | Agent profile, manage listings, view received buyer leads, handle visits |
| **Admin** | `admin@99hectares.com` | `admin123` | Backoffice review: approve properties, verify agents/builders, unlock leads |

---

## 2. Global Response Envelope & Status Codes

All API endpoints return standard, predictable JSON structures.

### 2.1 Single Item or Operation Success (`SuccessResponse<T>`)
```json
{
  "success": true,
  "message": "Property retrieved successfully",
  "data": {
    "id": 101,
    "title": "Luxury 3 BHK Apartment in Sector 62",
    "price": "14500000.00"
  }
}
```

### 2.2 Paginated List Response (`PaginatedResponse<T>`)
```json
{
  "success": true,
  "data": [
    { "id": 1, "title": "4 BHK Villa in Gurgaon", "price": "35000000.00" },
    { "id": 2, "title": "2 BHK Affordable Flat", "price": "4500000.00" }
  ],
  "total": 142,
  "page": 1,
  "page_size": 20,
  "total_pages": 8
}
```

### 2.3 Error Response Format (`ErrorResponse`)
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Property with ID 999 not found",
    "details": null
  }
}
```

### 2.4 HTTP Status Codes Summary
- `200 OK`: Request succeeded.
- `201 Created`: Resource successfully created.
- `400 Bad Request`: Business rule violation (e.g. "Property already favorited").
- `401 Unauthorized`: Missing, expired, or invalid JWT token.
- `403 Forbidden`: Insufficient role permissions (e.g. buyer attempting admin actions).
- `404 Not Found`: Resource does not exist.
- `422 Unprocessable Entity`: Request body or query validation failed.
- `500 Internal Server Error`: Unexpected server issue.

---

## 3. Authentication & Session Management

All protected endpoints require an `Authorization` header containing the JWT Bearer token:
```http
Authorization: Bearer <access_token>
```

### 3.1 Register New Account
- **Endpoint**: `POST /api/v1/auth/register`
- **Access**: Public
- **Request Body**:
```json
{
  "full_name": "Rohan Sharma",
  "email": "rohan@example.com",
  "phone": "+919876543210",
  "password": "Password123!",
  "role": "buyer"
}
```
> Note: `role` can be `"buyer"`, `"agent"`, or `"builder"`. Default is `"buyer"`.

- **Response (`200 OK`)**:
```json
{
  "success": true,
  "message": "Registration successful",
  "data": {
    "access_token": "eyJhbGciOi...",
    "refresh_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
      "id": 12,
      "email": "rohan@example.com",
      "full_name": "Rohan Sharma",
      "role": "buyer",
      "is_active": true,
      "is_verified": false
    }
  }
}
```

### 3.2 Login with Email & Password
- **Endpoint**: `POST /api/v1/auth/login`
- **Access**: Public
- **Request Body**:
```json
{
  "email": "aditya.mehta@example.com",
  "password": "password123"
}
```
- **Response (`200 OK`)**: Returns access token, refresh token, expiry seconds, and user profile object.

### 3.3 Refresh Access Token
- **Endpoint**: `POST /api/v1/auth/refresh`
- **Access**: Public
- **Request Body**:
```json
{
  "refresh_token": "eyJhbGciOi..."
}
```
- **Response (`200 OK`)**: Returns new `access_token` and `refresh_token`.

### 3.4 Logout
- **Endpoint**: `POST /api/v1/auth/logout`
- **Access**: Public
- **Request Body**:
```json
{
  "refresh_token": "eyJhbGciOi..."
}
```

### 3.5 OTP Login & Signup
1. **Request OTP**: `POST /api/v1/auth/otp/send`
   - Body: `{"phone": "+919876543210"}`
2. **Verify OTP & Authenticate**: `POST /api/v1/auth/otp/verify`
   - Body: `{"phone": "+919876543210", "otp": "123456"}`
   - Returns: `TokenResponse`

### 3.6 Forgot Password Flow
1. **Request Reset**: `POST /api/v1/auth/forgot-password/request`
   - Body: `{"email": "user@example.com"}`
2. **Confirm Reset**: `POST /api/v1/auth/forgot-password/confirm`
   - Body: `{"email": "user@example.com", "otp": "123456", "new_password": "NewPassword123!"}`

### 3.7 Change Password (Authenticated)
- **Endpoint**: `POST /api/v1/auth/change-password`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
```json
{
  "current_password": "OldPassword123!",
  "new_password": "NewStrongPassword123!"
}
```

### 3.8 Upgrade Account to Agent / Property Dealer
- **Endpoint**: `POST /api/v1/auth/become-agent`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
```json
{
  "agency_name": "Prime Realty Advisors",
  "license_number": "RERA-UP-123456",
  "experience_years": 5,
  "city_id": 1,
  "service_areas": ["Noida", "Greater Noida"],
  "address": "Office 401, Sector 18, Noida"
}
```

---

## 4. Properties & Listings

### 4.1 Search & Filter Properties (99acres-Style)
- **Endpoint**: `GET /api/v1/properties`
- **Access**: Public
- **Query Parameters**:
| Parameter | Type | Example | Description |
| :--- | :--- | :--- | :--- |
| `search` | string | `"Sector 62"` | Keyword search across title, description, address, city, and locality |
| `property_type`| string | `"apartment"` | `"apartment"`, `"independent_house"`, `"villa"`, `"plot"`, `"commercial"`, `"office"` |
| `listing_type` | string | `"SELL"` | `"SELL"` or `"RENT"` |
| `city_id` | integer| `1` | ID from Locations City endpoint |
| `locality_id` | integer| `5` | ID from Locations Locality endpoint |
| `min_price` | number | `5000000` | Minimum price (in INR) |
| `max_price` | number | `20000000` | Maximum price (in INR) |
| `bedrooms` | integer| `3` | Number of bedrooms (BHK) |
| `bathrooms` | integer| `2` | Minimum bathrooms |
| `furnishing_status`| string | `"SEMI_FURNISHED"` | `"UNFURNISHED"`, `"SEMI_FURNISHED"`, `"FURNISHED"` |
| `possession_status`| string | `"READY_TO_MOVE"` | `"READY_TO_MOVE"`, `"UNDER_CONSTRUCTION"` |
| `is_verified` | boolean| `true` | Show only platform-verified properties |
| `is_featured` | boolean| `true` | Show featured listings |
| `sort_by` | string | `"newest"` | `"newest"`, `"price_asc"`, `"price_desc"`, `"area_asc"`, `"area_desc"` |
| `page` | integer| `1` | Page number (starts at 1) |
| `page_size` | integer| `20` | Page size (max 100) |

- **Response (`200 OK`)**: Returns `PaginatedResponse<PropertyResponse>`.

### 4.2 Get Property Details by ID or Slug
- **Endpoint**: `GET /api/v1/properties/{id_or_slug}`
- **Access**: Public
- **Example**: `GET /api/v1/properties/309` or `GET /api/v1/properties/luxury-3bhk-noida-309`
- **Response (`200 OK`)**: Returns `SuccessResponse<PropertyDetailResponse>` with loaded media, amenities, residential/commercial details, agent/builder info, and location coordinates.

### 4.3 Create a Property Listing
- **Endpoint**: `POST /api/v1/properties`
- **Headers**: `Authorization: Bearer <token>`
- **Access**: Authenticated User (Owner), Agent, Builder, or Admin
- **Request Body**:
```json
{
  "title": "Spacious 3 BHK with Golf Course View",
  "description": "Corner unit, modular kitchen, wooden flooring in master bedroom.",
  "property_type": "apartment",
  "listing_type": "SELL",
  "price": 17500000,
  "currency": "INR",
  "maintenance_charges": 4500,
  "super_builtup_area": 1850,
  "carpet_area": 1420,
  "area_unit": "sqft",
  "bedrooms": 3,
  "bathrooms": 3,
  "balconies": 2,
  "furnishing_status": "SEMI_FURNISHED",
  "possession_status": "READY_TO_MOVE",
  "total_floors": 24,
  "floor_number": 14,
  "facing": "NORTH_EAST",
  "city_id": 1,
  "locality_id": 5,
  "address": "Tower 4, Green Arch, Sector 62",
  "latitude": 28.6280,
  "longitude": 77.3649
}
```

### 4.4 Update Property Listing
- **Endpoint**: `PUT /api/v1/properties/{id}`
- **Headers**: `Authorization: Bearer <token>`
- **Access**: Owner of property, assigned Agent, or Admin

### 4.5 Delete Property Listing
- **Endpoint**: `DELETE /api/v1/properties/{id}`
- **Headers**: `Authorization: Bearer <token>`

### 4.6 Upload Property Media (Images / Floor Plans / Videos)
- **Endpoint**: `POST /api/v1/properties/{id}/media`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
```json
{
  "media_type": "IMAGE",
  "url": "https://cdn.example.com/properties/img_123.jpg",
  "thumbnail_url": "https://cdn.example.com/properties/thumb_123.jpg",
  "title": "Living Room",
  "is_featured": true,
  "display_order": 1
}
```
> `media_type` values: `"IMAGE"`, `"FLOOR_PLAN"`, `"VIDEO"`, `"VIRTUAL_TOUR"`, `"BROCHURE"`.

### 4.7 Assign Amenities to Property
- **Endpoint**: `POST /api/v1/properties/{id}/amenities`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
```json
{
  "amenity_ids": [1, 2, 5, 8, 14]
}
```

---

## 5. Projects & Developments

### 5.1 List & Search Projects
- **Endpoint**: `GET /api/v1/projects`
- **Access**: Public
- **Query Parameters**: `search`, `city_id`, `locality_id`, `builder_id`, `status` (`"UPCOMING"`, `"UNDER_CONSTRUCTION"`, `"COMPLETED"`), `project_type`, `min_price`, `max_price`, `page`, `page_size`.

### 5.2 Get Project by ID or Slug
- **Endpoint**: `GET /api/v1/projects/{id_or_slug}`
- **Access**: Public

### 5.3 Create Project
- **Endpoint**: `POST /api/v1/projects`
- **Headers**: `Authorization: Bearer <token>`
- **Access**: Builder or Admin

---

## 6. Locations Hierarchy (Cascading Form Selectors)

Used for constructing dependent location dropdowns in search filters and property listing forms:
```
Country  ──>  State  ──>  City  ──>  Locality  ──>  Sub-Locality
```

| Hierarchy Level | Endpoint | Query Filters | Example Output Item |
| :--- | :--- | :--- | :--- |
| **1. Countries** | `GET /api/v1/locations/countries` | None | `{ "id": 1, "name": "India", "code": "IN" }` |
| **2. States** | `GET /api/v1/locations/states` | `?country_id=1` | `{ "id": 10, "name": "Uttar Pradesh" }` |
| **3. Cities** | `GET /api/v1/locations/cities` | `?state_id=10&search=Noida` | `{ "id": 1, "name": "Noida", "tier": "TIER_1" }` |
| **4. Localities** | `GET /api/v1/locations/localities` | `?city_id=1&search=Sector` | `{ "id": 5, "name": "Sector 62", "pincode": "201309" }` |
| **5. Sub-Localities** | `GET /api/v1/locations/sub-localities` | `?locality_id=5` | `{ "id": 22, "name": "Block B" }` |

---

## 7. Amenities Directory

- **Endpoint**: `GET /api/v1/amenities`
- **Access**: Public
- **Response**: List of all active platform amenities with `name`, `icon`, `category` (e.g. `"SAFETY"`, `"LUXURY"`, `"SPORTS"`, `"CONVENIENCE"`, `"ECO"`).

---

## 8. Favorites & Bookmarks (Shortlist)

Authenticated user's personal saved properties.

| Action | HTTP Method | Endpoint | Request Body / Params |
| :--- | :--- | :--- | :--- |
| **Get Favorites Count** | `GET` | `/api/v1/favorites/count` | *None* |
| **List Saved Properties** | `GET` | `/api/v1/favorites/` | *None* |
| **Add to Favorites** | `POST` | `/api/v1/favorites/` | `{"property_id": 309}` |
| **Check Favorite by Property** | `GET` | `/api/v1/favorites/{property_id}`| *Path param* |
| **Remove from Favorites** | `DELETE`| `/api/v1/favorites/{property_id}`| *Path param* |

---

## 9. Inquiries & Lead Generation

### 9.1 Submit an Inquiry (Buyer)
- **Endpoint**: `POST /api/v1/inquiries`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
```json
{
  "property_id": 309,
  "message": "Hi, I am interested in this 3 BHK flat. Please contact me regarding the best price.",
  "preferred_contact_method": "PHONE",
  "preferred_time": "EVENING"
}
```

### 9.2 View Submitted Inquiries (Buyer)
- **Endpoint**: `GET /api/v1/inquiries/my`
- **Headers**: `Authorization: Bearer <token>`

### 9.3 View Received Leads (Agent / Property Owner)
- **Endpoint**: `GET /api/v1/inquiries/received`
- **Headers**: `Authorization: Bearer <token>`
> Note: For listings managed through platform gatekeeper rules, buyer contact details (phone/email) are revealed once approved or unlocked by the admin.

### 9.4 Update Inquiry Status / Message
- **Endpoint**: `PATCH /api/v1/inquiries/{id}`
- **Request Body**: `{"message": "Updated details", "status": "IN_PROGRESS"}`

---

## 10. Site Visits & Scheduling

### 10.1 Request a Site Visit (Buyer)
- **Endpoint**: `POST /api/v1/visits`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
```json
{
  "property_id": 309,
  "requested_date": "2026-10-15T11:00:00Z",
  "user_notes": "Please arrange the key with society gate security."
}
```

### 10.2 View User's Visits (Buyer)
- **Endpoint**: `GET /api/v1/visits/user/{user_id}`
- **Headers**: `Authorization: Bearer <token>`

### 10.3 View Agent's Visits (Agent)
- **Endpoint**: `GET /api/v1/visits/agent/{agent_id}`
- **Headers**: `Authorization: Bearer <token>`

### 10.4 Update Visit Status (Confirm / Reschedule / Cancel)
- **Endpoint**: `PATCH /api/v1/visits/{id}/status`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
```json
{
  "status": "CONFIRMED",
  "confirmed_date": "2026-10-15T11:30:00Z",
  "agent_notes": "Confirmed with owner. Will meet at clubhouse."
}
```
> Supported `status` transitions: `"REQUESTED"`, `"CONFIRMED"`, `"COMPLETED"`, `"CANCELLED"`, `"REJECTED"`.

### 10.5 Delete / Cancel Visit Request
- **Endpoint**: `DELETE /api/v1/visits/{id}`
- **Headers**: `Authorization: Bearer <token>`

---

## 11. Agents & Builders Portals

### 11.1 Public Directory
- `GET /api/v1/agents?search=Sharma&city_id=1&page=1`
- `GET /api/v1/agents/{id}`
- `GET /api/v1/agents/{id}/properties`
- `GET /api/v1/builders?search=Godrej&page=1`
- `GET /api/v1/builders/{id}`

### 11.2 Authenticated Agent Portal
- **Profile**: `GET /api/v1/agents/me`, `PUT /api/v1/agents/me`
- **Listings**: `GET /api/v1/agents/me/properties`
- **Create Property Listing**: `POST /api/v1/agents/me/properties`
- **Bulk Upload Properties**: `POST /api/v1/agents/me/properties/bulk`

### 11.3 Authenticated Builder Portal
- **Profile**: `GET /api/v1/builders/me`, `PUT /api/v1/builders/me`

---

## 12. User Profile Management

- **Get Profile**: `GET /api/v1/users/me`
- **Update Profile**: `PUT /api/v1/users/me`
  - Body: `{"first_name": "Aditya", "last_name": "Mehta", "avatar_url": "https://..."}`
- **Public User Profile**: `GET /api/v1/users/{id}`

---

## 13. Reports & Dispute Resolution

- **Submit Report / Complaint**: `POST /api/v1/reports`
```json
{
  "property_id": 309,
  "reason": "MISLEADING_PRICE",
  "description": "Broker quoted 2.1 Cr on call instead of 1.75 Cr listed on site."
}
```
- **My Submitted Reports**: `GET /api/v1/reports/my`

---

## 14. Admin Control Panel

Accessible only with an Admin account (`admin@99hectares.com`):

| Operation | Method | Endpoint | Description |
| :--- | :--- | :--- | :--- |
| **List All Users** | `GET` | `/api/v1/admin/users` | Filters: `role`, `is_active`, `search`, `page` |
| **List All Properties** | `GET` | `/api/v1/admin/properties` | View pending, active, rejected listings |
| **Approve Property** | `PATCH` | `/api/v1/admin/properties/{id}/approve` | Publishes listing to public feed |
| **Reject Property** | `PATCH` | `/api/v1/admin/properties/{id}/reject` | Body: `{"reason": "Invalid documents"}` |
| **Verify Agent** | `PATCH` | `/api/v1/admin/agents/{id}/verify` | Body: `{"verification_status": "VERIFIED"}` |
| **Verify Builder** | `PATCH` | `/api/v1/admin/builders/{id}/verify` | Body: `{"verification_status": "VERIFIED"}` |
| **Manage Inquiries (Leads)**| `GET` | `/api/v1/admin/inquiries` | Review leads and payment status |
| **Approve Lead Payment** | `PATCH` | `/api/v1/admin/inquiries/{id}/approve` | Unlocks buyer contact details for recipient |
| **Reject Lead** | `PATCH` | `/api/v1/admin/inquiries/{id}/reject` | Reject lead request |
| **Resolve Report** | `PATCH` | `/api/v1/admin/reports/{id}/resolve` | Body: `{"admin_notes": "Listing updated"}` |

---

## 15. TypeScript Definitions

Copy this directly into your frontend `src/types/api.ts`:

```typescript
export type UserRole = "buyer" | "agent" | "builder" | "admin";

export interface User {
  id: number;
  email: string;
  phone?: string | null;
  full_name?: string | null;
  first_name?: string | null;
  last_name?: string | null;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  avatar_url?: string | null;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
  expires_in: number;
  user: User;
}

export interface LocationCity {
  id: number;
  name: string;
  state_id: number;
  tier?: string | null;
}

export interface LocationLocality {
  id: number;
  name: string;
  city_id: number;
  pincode?: string | null;
}

export interface PropertyMedia {
  id: number;
  property_id: number;
  media_type: "IMAGE" | "FLOOR_PLAN" | "VIDEO" | "VIRTUAL_TOUR" | "BROCHURE";
  url: string;
  thumbnail_url?: string | null;
  title?: string | null;
  is_featured: boolean;
  display_order: number;
}

export interface Amenity {
  id: number;
  name: string;
  icon?: string | null;
  category: string;
  is_active: boolean;
}

export interface Property {
  id: number;
  title: string;
  slug: string;
  description?: string | null;
  property_type: string;
  listing_type: "SELL" | "RENT";
  status: "DRAFT" | "PENDING" | "ACTIVE" | "REJECTED" | "SOLD";
  price: number | string;
  currency: string;
  maintenance_charges?: number | null;
  super_builtup_area?: number | null;
  carpet_area?: number | null;
  area_unit: string;
  bedrooms?: number | null;
  bathrooms?: number | null;
  balconies?: number | null;
  furnishing_status?: string | null;
  possession_status?: string | null;
  total_floors?: number | null;
  floor_number?: number | null;
  facing?: string | null;
  address?: string | null;
  city_id: number;
  locality_id?: number | null;
  city?: LocationCity | null;
  locality?: LocationLocality | null;
  media: PropertyMedia[];
  amenities?: Amenity[];
  is_verified: boolean;
  is_featured: boolean;
  is_active: boolean;
  created_at: string;
  published_at?: string | null;
}

export interface Inquiry {
  id: number;
  user_id: number;
  property_id?: number | null;
  project_id?: number | null;
  agent_id?: number | null;
  builder_id?: number | null;
  message: string;
  status: "NEW" | "IN_PROGRESS" | "CONTACTED" | "CLOSED";
  is_admin_approved: boolean;
  preferred_contact_method?: string | null;
  preferred_time?: string | null;
  created_at: string;
}

export interface Visit {
  id: number;
  user_id: number;
  property_id: number;
  agent_id?: number | null;
  requested_date: string;
  confirmed_date?: string | null;
  status: "REQUESTED" | "CONFIRMED" | "COMPLETED" | "CANCELLED" | "REJECTED";
  user_notes?: string | null;
  agent_notes?: string | null;
  cancellation_reason?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ApiResponse<T> {
  success: boolean;
  message?: string;
  data: T;
}

export interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
```

---

## 16. Production Axios Client Template (With Auto-Refresh)

Save this as `src/api/client.ts`:

```typescript
import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 15000,
});

// Request interceptor: Attach access token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("access_token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: Auto refresh token on 401
let isRefreshing = false;
let failedQueue: Array<{ resolve: (token: string) => void; reject: (err: any) => void }> = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((promise) => {
    if (error) {
      promise.reject(error);
    } else if (token) {
      promise.resolve(token);
    }
  });
  failedQueue = [];
};

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (typeof window === "undefined") {
        return Promise.reject(error);
      }

      const refreshToken = localStorage.getItem("refresh_token");
      if (!refreshToken) {
        localStorage.clear();
        window.location.href = "/login";
        return Promise.reject(error);
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({
            resolve: (token: string) => {
              originalRequest.headers.Authorization = `Bearer ${token}`;
              resolve(apiClient(originalRequest));
            },
            reject: (err: any) => reject(err),
          });
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        });

        const { access_token, refresh_token: newRefreshToken } = response.data.data;
        localStorage.setItem("access_token", access_token);
        if (newRefreshToken) {
          localStorage.setItem("refresh_token", newRefreshToken);
        }

        apiClient.defaults.headers.common.Authorization = `Bearer ${access_token}`;
        processQueue(null, access_token);

        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return apiClient(originalRequest);
      } catch (refreshErr) {
        processQueue(refreshErr, null);
        localStorage.clear();
        window.location.href = "/login";
        return Promise.reject(refreshErr);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);
```
