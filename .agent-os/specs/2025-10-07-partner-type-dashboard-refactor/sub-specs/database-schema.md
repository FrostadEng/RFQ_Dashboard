# Database Schema

This is the database schema implementation for the spec detailed in @.agent-os/specs/2025-10-07-partner-type-dashboard-refactor/spec.md

## Schema Changes

### 1. `suppliers` Collection

#### New Field
Add the following field to the `suppliers` collection:

```javascript
{
  partner_type: {
    type: String,
    enum: ['Supplier', 'Contractor'],
    default: 'Supplier',
    required: true
  }
}
```

#### Rationale
- The `partner_type` field distinguishes between traditional suppliers (material/equipment vendors) and contractors (subcontractors bidding on work packages)
- Default value of 'Supplier' ensures backward compatibility with existing documents
- Enum constraint prevents invalid values and ensures data integrity

### 2. `submissions` Collection

#### New Field
Add the following field to the `submissions` collection (also referred to as `transmissions` and `receipts` in the codebase):

```javascript
{
  partner_type: {
    type: String,
    enum: ['Supplier', 'Contractor'],
    default: 'Supplier',
    required: true
  }
}
```

#### Rationale
- Denormalizing `partner_type` into submissions enables efficient filtering without joins
- Each submission inherits the partner_type from its parent partner
- Simplifies aggregation queries for project-level statistics

## Indexes

### Recommended Indexes

#### `suppliers` Collection
```javascript
db.suppliers.createIndex({ "partner_type": 1 })
db.suppliers.createIndex({ "project_id": 1, "partner_type": 1 })
```

#### `submissions` Collection
```javascript
db.submissions.createIndex({ "partner_type": 1 })
db.submissions.createIndex({ "project_id": 1, "partner_type": 1 })
db.submissions.createIndex({ "project_id": 1, "partner_type": 1, "direction": 1 })
```

#### Rationale
- Single-field index on `partner_type` speeds up filtering queries in the UI toggle
- Compound indexes on `project_id` + `partner_type` optimize the most common query pattern (filtering by project and partner type)
- Three-field compound index on submissions supports efficient aggregation for sent/received counts

## Migration Strategy

### Approach: Lazy Migration via Crawler

No explicit migration script is required. The crawler will populate the `partner_type` field on its next scan:

1. **New Scans**: All newly discovered partners/submissions will have `partner_type` set based on folder structure detection
2. **Existing Documents**: Documents without `partner_type` will be treated as 'Supplier' (application-level default)
3. **Re-scans**: When the crawler re-scans existing projects, it will update documents with the correct `partner_type`

### Rationale
- Avoids the complexity of writing and testing a one-time migration script
- Aligns with the crawler's role as the authoritative source of file system data
- Existing UI functionality remains unaffected (defaults to 'Supplier' behavior)
- Natural convergence to full data population over time as projects are re-scanned

## Data Integrity Rules

### Constraints
1. `partner_type` must be one of: 'Supplier' or 'Contractor'
2. `partner_type` on a submission must match the `partner_type` of its parent partner
3. All queries filtering by partner type must handle missing values gracefully (treat as 'Supplier')

### Validation
- Application-level validation in the crawler ensures consistent assignment
- MongoDB schema validation (if enabled) enforces enum constraint
- UI queries include fallback logic: `{"partner_type": {"$in": [selected_type, null]}}` during transition period
