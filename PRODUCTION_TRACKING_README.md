# Production Item Tracking Module

A comprehensive ERPNext module for tracking production workflow items through multiple stages (Painter, Embellisher, Tailor, Dyer, etc.) with deadline management and performance analytics.

## Features

### Phase 1: Core Tracking ✅
- **Production Item Tracking DocType**: Track each item's journey through production
- **Assignment History**: Complete audit trail of all assignments and transfers
- **Automatic Deadline Calculation**: Auto-calculate expected completion dates
- **Overdue Detection**: Automatic flagging of overdue items with days count
- **Manual Status Updates**: Full control over item status and assignments

### Phase 2: Enhanced UX ✅
- **Timeline Visualization Page**: Visual representation of production progress
- **Bulk Operations**: Assign multiple items to workers at once
- **Quick Update Actions**: Inline status updates from timeline view
- **Performance Reports**:
  - Overdue Items Report
  - Worker Performance Report
  - Customer Order Status Report

## Installation

1. Install the app in your Frappe/ERPNext bench:
```bash
bench get-app nisa /path/to/nisa
bench --site your-site.local install-app nisa
```

2. After installation, migrate the site:
```bash
bench --site your-site.local migrate
```

3. Clear cache and build:
```bash
bench --site your-site.local clear-cache
bench build
```

## Setup

### 1. Configure Supplier Groups

Before using the system, set up supplier groups for your workers:

1. Go to **Buying > Supplier Group**
2. Create the following groups:
   - Painter
   - Embellisher
   - Tailor
   - Dyer

### 2. Add Suppliers (Workers)

1. Go to **Buying > Supplier**
2. Create suppliers for each worker
3. Assign them to appropriate Supplier Groups created above

Example:
- Name: Ali Painting Works
- Supplier Group: Painter

## Usage Guide

### Creating Item Tracking Records

#### Method 1: Manual Creation

1. Go to **Nisa > Production Item Tracking**
2. Click **New**
3. Select **Sales Order** (automatically fetches customer and delivery date)
4. Select **Item Code** from the sales order
5. Click **Save**

#### Method 2: Auto-populate from Sales Order

When you select a Sales Order, the system will show a dialog to select which item from the order you want to track.

### Workflow Operations

#### 1. Assign to Worker

1. Open a Production Item Tracking document
2. Click **Actions > Assign to Worker**
3. Fill in:
   - Process Type (Painter, Embellisher, etc.)
   - Assign To (select worker/supplier)
   - Required Days (deadline)
   - Remarks (optional)
4. Click **Assign**

The system will:
- Update current assignment
- Calculate expected completion date
- Add entry to assignment history
- Set status to "In Progress"

#### 2. Mark Received

When you receive an item from a worker:

1. Open the tracking document
2. Click **Actions > Mark Received**
3. Add remarks if needed
4. Click **Submit**

This updates the status to "In Progress" in the history.

#### 3. Complete Process

When a worker completes their task:

1. Open the tracking document
2. Click **Actions > Complete Process**
3. Add remarks if needed
4. Click **Submit**

The system will:
- Mark the current process as completed
- Calculate actual days taken
- Update completion date

#### 4. Transfer to Next

To complete current process and assign to next worker in one step:

1. Open the tracking document
2. Click **Actions > Transfer to Next**
3. Fill in:
   - Next Process
   - Next Assignee
   - Required Days
   - Remarks (optional)
4. Click **Transfer**

### Bulk Operations

To assign multiple items to the same worker:

1. Go to **Nisa > Production Item Tracking** list
2. Check the items you want to assign
3. Click **Bulk Assign** button
4. Fill in assignment details
5. Click **Assign All**

### Timeline Visualization

Access the visual timeline view:

1. Go to **Nisa > Production Timeline**
2. Use filters to narrow down:
   - Customer
   - Sales Order
   - Status
   - Current Process
3. View the timeline showing each item's progress
4. Use **Quick Update** button for inline status changes

The timeline shows:
- ✓ Completed processes (green circles)
- ● Current process (blue circles)
- ○ Pending processes (gray circles)
- Worker names and days taken
- Overdue badges

## Reports

### 1. Overdue Production Items

**Path**: Nisa > Overdue Production Items

Shows all items past their expected completion date.

**Filters**:
- Customer
- Sales Order
- Current Process
- Current Assignee
- Date Range

**Use Case**: Daily follow-up on delayed items

### 2. Worker Performance

**Path**: Nisa > Worker Performance

Analytics on worker efficiency and performance.

**Columns**:
- Worker name
- Process type
- Total assignments
- Completed/In Progress/Overdue counts
- Average days taken
- Completion rate %

**Use Case**: Performance reviews, identifying bottlenecks

### 3. Customer Order Status

**Path**: Nisa > Customer Order Status

Overview of all sales orders with completion status.

**Columns**:
- Sales Order
- Customer
- Delivery Date
- Total/Completed/In Progress/Overdue items
- Completion percentage
- Order status

**Use Case**: Customer communication, priority planning

## Field Descriptions

### Production Item Tracking

| Field | Description |
|-------|-------------|
| Sales Order | Link to sales order |
| Customer | Auto-fetched from sales order |
| Item Code | Item being tracked |
| Current Process | Which stage item is at |
| Current Assignee | Who currently has the item |
| Assigned Date | When current assignment started |
| Required Days | Deadline duration |
| Expected Completion Date | Auto-calculated deadline |
| Actual Completion Date | When fully completed |
| Overall Status | Not Started/In Progress/Completed/Overdue |
| Is Overdue | Auto-flag for overdue items |
| Days Overdue | How many days past deadline |

### Item Assignment History (Child Table)

| Field | Description |
|-------|-------------|
| Process Type | Stage of production |
| Assigned To | Worker name |
| Assigned Date | When assigned |
| Expected Date | Deadline for this stage |
| Received Date | When completed |
| Days Taken | Actual duration |
| Status | Assigned/In Progress/Completed |
| Remarks | Notes and comments |

## Auto-Calculations

The system automatically calculates:

1. **Expected Completion Date**: `Assigned Date + Required Days`
2. **Required Days**: If you set expected date, it calculates required days
3. **Is Overdue**: Flags if today > expected date
4. **Days Overdue**: `Today - Expected Completion Date`
5. **Days Taken**: `Received Date - Assigned Date`
6. **Overall Status**: Based on completion and overdue status

## Permissions

Default roles with access:

- **System Manager**: Full access
- **Manufacturing Manager**: Full access
- **Manufacturing User**: Read-only access

Customize permissions via Role Permission Manager if needed.

## Tips & Best Practices

1. **Daily Reviews**: Check "Overdue Production Items" report daily
2. **Bulk Assignments**: Use bulk assign for efficiency when same batch goes to one worker
3. **Timeline View**: Use for customer calls to show real-time progress
4. **Remarks**: Always add remarks when transferring - helps with tracking issues
5. **Worker Performance**: Review monthly for process improvement
6. **Deadline Setting**: Set realistic required days per process based on historical data

## Troubleshooting

### Items not showing in Timeline
- Check if filters are too restrictive
- Ensure items have been assigned at least once

### Can't assign to worker
- Verify worker is set up as Supplier
- Check supplier group is correctly set
- Ensure you have write permissions

### Dates not calculating
- Ensure Assigned Date is filled
- Enter Required Days or Expected Completion Date
- Save the document to trigger calculations

## API Methods

For custom scripts or integrations:

```python
# Assign item to worker
frappe.call({
    method: 'nisa.nisa.doctype.production_item_tracking.production_item_tracking.assign_to_worker',
    args: {
        doc_name: 'PIT-SO-001-ITEM-0001',
        process_type: 'Painter',
        assignee: 'SUP-00001',
        required_days: 5,
        remarks: 'Rush order'
    }
})

# Transfer to next process
frappe.call({
    method: 'nisa.nisa.doctype.production_item_tracking.production_item_tracking.transfer_to_next',
    args: {
        doc_name: 'PIT-SO-001-ITEM-0001',
        next_process: 'Embellisher',
        next_assignee: 'SUP-00002',
        required_days: 3
    }
})

# Get overdue items
frappe.call({
    method: 'nisa.nisa.doctype.production_item_tracking.production_item_tracking.get_overdue_items',
    callback: function(r) {
        console.log(r.message);
    }
})
```

## Support

For issues or feature requests, please contact your system administrator.

## License

MIT
