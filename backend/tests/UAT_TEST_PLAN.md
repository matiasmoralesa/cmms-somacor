# User Acceptance Testing (UAT) Plan
## CMMS Sistema Avanzado

### Overview
This document outlines the user acceptance testing scenarios for the CMMS system. Each scenario tests a complete user workflow from start to finish.

---

## Test Environment Setup

### Prerequisites
1. Backend API running on `http://localhost:8000`
2. Frontend app running on `http://localhost:5173`
3. Demo data loaded: `python manage.py generate_demo_data`
4. Test users created with credentials

### Test Credentials

| Role | Email | Password | Purpose |
|------|-------|----------|---------|
| Admin | admin@somacor.com | Demo2024! | Full system access |
| Supervisor | supervisor1@somacor.com | Demo2024! | Maintenance management |
| Operator | operator1@somacor.com | Demo2024! | Field operations |

---

## UAT Scenario 1: Complete Work Order Lifecycle

**User Role:** Supervisor + Operator  
**Duration:** 15 minutes  
**Objective:** Test the complete workflow from work order creation to completion

### Steps:

#### Part A: Supervisor Creates Work Order
1. Login as `supervisor1@somacor.com`
2. Navigate to "Órdenes de Trabajo" (Work Orders)
3. Click "Nueva Orden" (New Order)
4. Fill in the form:
   - Title: "Mantenimiento preventivo - Camioneta MDO 001"
   - Description: "Cambio de aceite y filtros"
   - Asset: Select "Camioneta MDO 001"
   - Type: "Preventivo"
   - Priority: "Media"
   - Assigned to: Select "Pedro Operador"
   - Scheduled date: Tomorrow's date
5. Click "Guardar" (Save)
6. Verify work order appears in the list with status "Pendiente"
7. Verify work order number is auto-generated (e.g., WO-2024-XXX)

**Expected Results:**
- ✅ Work order created successfully
- ✅ Work order number auto-generated
- ✅ Status is "Pendiente"
- ✅ Notification sent to assigned operator

#### Part B: Operator Views and Starts Work Order
1. Logout and login as `operator1@somacor.com`
2. Navigate to "Mis Asignaciones" (My Assignments)
3. Verify the new work order appears in the list
4. Click on the work order to view details
5. Click "Iniciar Trabajo" (Start Work)
6. Verify status changes to "En Progreso"

**Expected Results:**
- ✅ Work order visible in operator's assignments
- ✅ Status changes to "En Progreso"
- ✅ Start time is recorded
- ✅ Notification sent to supervisor

#### Part C: Operator Completes Work Order
1. While viewing the work order, click "Completar" (Complete)
2. Fill in completion form:
   - Actual hours: 2.5
   - Completion notes: "Cambio de aceite y filtros completado. Todo OK."
3. Click "Guardar" (Save)
4. Verify status changes to "Completado"
5. Verify completion timestamp is recorded

**Expected Results:**
- ✅ Work order marked as completed
- ✅ Actual hours recorded
- ✅ Completion notes saved
- ✅ Completion timestamp recorded
- ✅ Notification sent to supervisor

---

## UAT Scenario 2: Checklist Execution with Mobile Interface

**User Role:** Operator  
**Duration:** 10 minutes  
**Objective:** Test checklist completion with photo uploads and digital signature

### Steps:

1. Login as `operator1@somacor.com`
2. Navigate to "Checklists"
3. Click "Nueva Inspección" (New Inspection)
4. Select template: "Check List Camionetas MDO (F-PR-020-CH01)"
5. Select asset: "Camioneta MDO 001"
6. Link to work order (optional): Select existing work order
7. Complete checklist items:
   - Item 1 (Nivel de aceite motor): Select "Sí"
   - Item 2 (Nivel de refrigerante): Select "Sí", add note "Nivel correcto"
   - Item 3 (Estado de pastillas de freno): Select "No", add note "Requiere cambio pronto"
   - Item 4 (Presión de neumáticos): Enter "32" PSI
   - Item 5 (Funcionamiento de luces): Select "Sí"
8. Upload photo for Item 3 (brake pads)
9. Add digital signature
10. Click "Finalizar Inspección" (Finish Inspection)
11. Verify score is calculated
12. Download generated PDF report

**Expected Results:**
- ✅ Checklist template loads correctly
- ✅ All item types work (yes/no, numeric, text)
- ✅ Photo upload successful
- ✅ Digital signature captured
- ✅ Score calculated correctly (80% passing threshold)
- ✅ PDF generated matching original format
- ✅ PDF stored in Cloud Storage
- ✅ Checklist linked to work order

---

## UAT Scenario 3: Maintenance Plan Execution

**User Role:** Supervisor  
**Duration:** 12 minutes  
**Objective:** Test maintenance plan creation and automatic work order generation

### Steps:

#### Part A: Create Maintenance Plan
1. Login as `supervisor1@somacor.com`
2. Navigate to "Planes de Mantenimiento" (Maintenance Plans)
3. Click "Nuevo Plan" (New Plan)
4. Fill in the form:
   - Name: "Inspección Semanal - Retroexcavadora"
   - Asset: "Retroexcavadora MDO 001"
   - Type: "Preventivo"
   - Recurrence: "Semanal"
   - Interval: 1 week
   - Next due date: 7 days from today
   - Checklist template: "Check Retroexcavadora MDO"
   - Estimated duration: 90 minutes
5. Click "Guardar" (Save)
6. Verify plan appears in active plans list

**Expected Results:**
- ✅ Maintenance plan created
- ✅ Next due date calculated correctly
- ✅ Plan status is "Activo"
- ✅ Checklist template linked

#### Part B: Simulate Automatic Work Order Generation
1. Navigate to "Órdenes de Trabajo"
2. Verify that when the due date arrives, a work order is automatically created
   - (In production, this is done by Cloud Composer DAG)
   - For testing, manually create a work order referencing the plan
3. Verify work order has:
   - Title includes plan name
   - Type is "Preventivo"
   - Asset matches plan
   - Checklist template attached

**Expected Results:**
- ✅ Work order generated from plan
- ✅ All plan details transferred to work order
- ✅ Checklist template attached

#### Part C: Pause and Resume Plan
1. Navigate back to maintenance plans
2. Select the created plan
3. Click "Pausar Plan" (Pause Plan)
4. Verify status changes to "Pausado"
5. Click "Reanudar Plan" (Resume Plan)
6. Verify status changes back to "Activo"

**Expected Results:**
- ✅ Plan can be paused
- ✅ Plan can be resumed
- ✅ Status updates correctly
- ✅ Historical data preserved

---

## UAT Scenario 4: ML Prediction and Alert Workflow

**User Role:** Supervisor + Admin  
**Duration:** 10 minutes  
**Objective:** Test ML prediction generation and alert handling

### Steps:

#### Part A: View Predictions Dashboard
1. Login as `supervisor1@somacor.com`
2. Navigate to "Predicciones" (Predictions)
3. View the predictions dashboard
4. Verify health scores are displayed for all assets
5. Click on "Camión Supersucker 001" (high-risk asset)
6. View prediction details:
   - Failure probability: 82.5%
   - Risk level: CRITICAL
   - Predicted failure date
   - Recommendations

**Expected Results:**
- ✅ Dashboard displays all assets with health scores
- ✅ High-risk assets highlighted in red
- ✅ Prediction details visible
- ✅ Recommendations displayed

#### Part B: Handle Critical Alert
1. Navigate to "Alertas" (Alerts)
2. Verify critical alert appears for Supersucker
3. Click on the alert to view details
4. Click "Crear Orden de Trabajo" (Create Work Order)
5. Verify work order form pre-fills with:
   - Type: "Predictivo"
   - Priority: "Urgente"
   - Asset: Supersucker
   - Description includes prediction details
6. Assign to an operator and save
7. Return to alert and click "Resolver" (Resolve)
8. Add resolution notes: "Orden de trabajo creada y asignada"
9. Verify alert is marked as resolved

**Expected Results:**
- ✅ Critical alert visible
- ✅ Work order can be created from alert
- ✅ Work order pre-filled with prediction data
- ✅ Alert can be resolved
- ✅ Resolution tracked with user and timestamp

---

## UAT Scenario 5: Inventory Management and Low Stock Alerts

**User Role:** Operator + Supervisor  
**Duration:** 8 minutes  
**Objective:** Test spare parts management and low stock alerting

### Steps:

#### Part A: View Inventory
1. Login as `operator1@somacor.com`
2. Navigate to "Inventario" (Inventory)
3. View list of spare parts
4. Verify low stock items are highlighted (e.g., "Filtro de aire")
5. Click on a spare part to view details
6. View usage history

**Expected Results:**
- ✅ All spare parts displayed
- ✅ Low stock items highlighted
- ✅ Stock levels visible
- ✅ Usage history available

#### Part B: Adjust Stock
1. Select "Filtro de aceite motor"
2. Click "Ajustar Stock" (Adjust Stock)
3. Select movement type: "Salida" (Out)
4. Enter quantity: 5
5. Link to work order: Select recent work order
6. Add notes: "Usado en mantenimiento preventivo"
7. Click "Guardar" (Save)
8. Verify stock quantity decreased
9. Verify movement appears in history

**Expected Results:**
- ✅ Stock adjusted correctly
- ✅ Movement recorded in history
- ✅ Linked to work order
- ✅ Notes saved

#### Part C: Low Stock Alert
1. Adjust stock of "Neumático 275/70R18" to below minimum (e.g., 5 units)
2. Verify low stock alert is generated
3. Navigate to "Alertas"
4. Verify alert appears with severity "WARNING"
5. Verify alert message includes part name and current/minimum stock

**Expected Results:**
- ✅ Low stock alert generated automatically
- ✅ Alert visible in alerts list
- ✅ Alert includes relevant details
- ✅ Notification sent to supervisors

---

## UAT Scenario 6: Role-Based Access Control

**User Role:** All roles  
**Duration:** 10 minutes  
**Objective:** Verify role-based permissions are enforced

### Steps:

#### Part A: Operator Permissions
1. Login as `operator1@somacor.com`
2. Verify operator CAN:
   - View assigned work orders
   - Complete assigned work orders
   - Execute checklists
   - View inventory
   - View own notifications
3. Verify operator CANNOT:
   - Create work orders
   - Assign work orders to others
   - Create maintenance plans
   - View all work orders (only assigned ones)
   - Access admin panel
   - View ML predictions/alerts
   - Manage users

**Expected Results:**
- ✅ Operator has limited access
- ✅ Unauthorized actions return 403 Forbidden
- ✅ UI hides unauthorized features

#### Part B: Supervisor Permissions
1. Login as `supervisor1@somacor.com`
2. Verify supervisor CAN:
   - View all work orders
   - Create and assign work orders
   - Create maintenance plans
   - View predictions and alerts
   - Manage inventory
   - View all assets
3. Verify supervisor CANNOT:
   - Access admin panel
   - Manage users
   - Modify system configuration

**Expected Results:**
- ✅ Supervisor has management access
- ✅ Cannot access admin functions
- ✅ UI shows appropriate features

#### Part C: Admin Permissions
1. Login as `admin@somacor.com`
2. Verify admin CAN:
   - Access all features
   - Manage users and roles
   - Configure system settings
   - View audit logs
   - Manage master data

**Expected Results:**
- ✅ Admin has full access
- ✅ All features visible
- ✅ Admin panel accessible

---

## UAT Scenario 7: Telegram Bot Integration

**User Role:** All roles  
**Duration:** 12 minutes  
**Objective:** Test Telegram bot commands and notifications

### Steps:

#### Part A: Bot Authentication
1. Open Telegram and find the CMMS bot
2. Send `/start` command
3. Verify bot responds with welcome message
4. Verify bot recognizes user role based on Telegram ID

**Expected Results:**
- ✅ Bot responds to /start
- ✅ User authenticated
- ✅ Role recognized

#### Part B: Test Commands by Role
1. As Operator (`operator1`):
   - Send `/status` - verify system status
   - Send `/equipos` - verify assigned assets only
   - Send `/ordenes` - verify assigned work orders only
   - Send `/pendientes` - verify pending work order count
   - Send `/alertas` - verify permission denied
   - Send `/kpis` - verify permission denied

2. As Supervisor (`supervisor1`):
   - Send `/status` - verify system status
   - Send `/equipos` - verify all assets
   - Send `/ordenes` - verify all work orders
   - Send `/pendientes` - verify all pending work orders
   - Send `/alertas` - verify recent alerts
   - Send `/kpis` - verify KPIs (MTBF, MTTR, OEE)

3. As Admin (`admin`):
   - Send all commands - verify full access

**Expected Results:**
- ✅ All commands work correctly
- ✅ Role-based access enforced
- ✅ Data formatted properly
- ✅ Responses are clear and concise

#### Part C: Real-time Notifications
1. As Supervisor, create a new work order and assign to Operator
2. Verify Operator receives Telegram notification
3. Verify notification includes:
   - Work order title
   - Priority
   - Scheduled date
   - Link to view details

**Expected Results:**
- ✅ Notification received in Telegram
- ✅ Notification is timely (< 5 seconds)
- ✅ Notification includes relevant details
- ✅ Link works correctly

---

## UAT Scenario 8: Reports and Analytics

**User Role:** Supervisor + Admin  
**Duration:** 10 minutes  
**Objective:** Test report generation and KPI visualization

### Steps:

#### Part A: View Dashboard
1. Login as `supervisor1@somacor.com`
2. Navigate to "Reportes" (Reports)
3. View KPI dashboard
4. Verify KPI cards display:
   - Active work orders count
   - Pending maintenance count
   - Critical alerts count
   - Asset availability percentage
5. View charts:
   - Work orders by status (pie chart)
   - Work orders by priority (bar chart)
   - Asset health scores (line chart)
   - Maintenance completion trend (line chart)

**Expected Results:**
- ✅ All KPIs calculated correctly
- ✅ Charts render properly
- ✅ Data is accurate
- ✅ Interactive features work (hover, zoom)

#### Part B: Generate Custom Report
1. Click "Generar Reporte" (Generate Report)
2. Select report type: "Resumen de Órdenes de Trabajo"
3. Select date range: Last 30 days
4. Select filters:
   - Asset: All
   - Status: All
   - Priority: All
5. Click "Generar" (Generate)
6. Verify report displays:
   - Total work orders
   - Completion rate
   - Average completion time
   - Work orders by type
7. Click "Exportar CSV" (Export CSV)
8. Verify CSV file downloads correctly

**Expected Results:**
- ✅ Report generated successfully
- ✅ Data is accurate
- ✅ Filters work correctly
- ✅ CSV export works
- ✅ CSV contains all expected data

#### Part C: Scheduled Reports
1. Navigate to "Reportes Programados" (Scheduled Reports)
2. Click "Nuevo Reporte Programado" (New Scheduled Report)
3. Configure:
   - Report type: "KPIs Semanales"
   - Frequency: Weekly (Mondays at 8 AM)
   - Recipients: Add email addresses
   - Format: PDF
4. Click "Guardar" (Save)
5. Verify scheduled report appears in list

**Expected Results:**
- ✅ Scheduled report created
- ✅ Configuration saved correctly
- ✅ Report will be sent automatically (verify in Cloud Composer)

---

## UAT Scenario 9: Mobile Responsiveness

**User Role:** Operator  
**Duration:** 8 minutes  
**Objective:** Test mobile interface usability

### Steps:

1. Open browser in mobile view (or use actual mobile device)
2. Login as `operator1@somacor.com`
3. Test navigation:
   - Verify hamburger menu works
   - Navigate between sections
   - Verify all features accessible
4. Test work order view:
   - View work order list
   - View work order details
   - Start work order
   - Complete work order
5. Test checklist execution:
   - Open checklist
   - Complete items
   - Upload photo from camera
   - Add signature with touch
   - Submit checklist
6. Test notifications:
   - View notification bell
   - Read notifications
   - Mark as read

**Expected Results:**
- ✅ All features work on mobile
- ✅ UI is responsive and usable
- ✅ Touch interactions work
- ✅ Camera integration works
- ✅ No horizontal scrolling
- ✅ Text is readable
- ✅ Buttons are tappable

---

## UAT Scenario 10: System Performance and Reliability

**User Role:** All roles  
**Duration:** 15 minutes  
**Objective:** Test system performance under normal load

### Steps:

#### Part A: Response Time Testing
1. Login and measure time to dashboard load
2. Navigate to work orders list (100+ records)
3. Measure page load time
4. Apply filters and measure response time
5. Create new work order and measure save time
6. Upload document and measure upload time

**Expected Results:**
- ✅ Dashboard loads in < 2 seconds
- ✅ List pages load in < 1 second
- ✅ Filter responses in < 500ms
- ✅ Form submissions in < 1 second
- ✅ File uploads in < 3 seconds (for 5MB file)

#### Part B: Concurrent User Testing
1. Have 3 users login simultaneously
2. Each user performs different actions:
   - User 1: Creates work order
   - User 2: Completes checklist
   - User 3: Views reports
3. Verify no conflicts or errors
4. Verify all actions complete successfully

**Expected Results:**
- ✅ No errors with concurrent users
- ✅ Data consistency maintained
- ✅ No performance degradation

#### Part C: Offline Capability Testing
1. Login as operator on mobile
2. Disable network connection
3. Attempt to view cached work orders
4. Attempt to complete work order
5. Re-enable network connection
6. Verify data syncs automatically

**Expected Results:**
- ✅ Cached data accessible offline
- ✅ Offline actions queued
- ✅ Data syncs when online
- ✅ No data loss

---

## Test Completion Checklist

### Functional Testing
- [ ] All 10 UAT scenarios completed
- [ ] All expected results verified
- [ ] No critical bugs found
- [ ] All user roles tested
- [ ] All major features tested

### Non-Functional Testing
- [ ] Performance meets targets
- [ ] Mobile responsiveness verified
- [ ] Security controls working
- [ ] Data integrity maintained
- [ ] Error handling appropriate

### Documentation
- [ ] Test results documented
- [ ] Issues logged in tracking system
- [ ] User feedback collected
- [ ] Screenshots captured
- [ ] Sign-off obtained

---

## Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Product Owner | | | |
| QA Lead | | | |
| Technical Lead | | | |
| Business Stakeholder | | | |

---

## Notes and Issues

Use this section to document any issues, observations, or recommendations during UAT:

1. 
2. 
3. 

---

**Document Version:** 1.0  
**Last Updated:** 2024-11-13  
**Next Review:** After UAT completion
