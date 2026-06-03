# DentalAI - Quick Start Demo Guide

## 🚀 Complete Setup & Demo Instructions

This guide will help you set up DentalAI with realistic demo data for presentations and testing.

---

## Prerequisites

- Python 3.10+
- PostgreSQL (local or Docker)
- Redis (for Celery - optional)
- Node.js 18+ (for frontend)

---

## 1. Database Setup

### Option A: Using Docker (Recommended)

```bash
# Start PostgreSQL and Redis with Docker
docker-compose up -d postgres redis

# Wait for database to be ready
sleep 5
```

### Option B: Local PostgreSQL

```bash
# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE dentalai;
CREATE USER dentalai WITH PASSWORD 'dentalai_dev';
GRANT ALL PRIVILEGES ON DATABASE dentalai to dentalai;
EOF
```

---

## 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment (if not already done)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Seed demo data
python manage.py seed_demo_data

# Start backend server
python manage.py runserver
```

Backend will be available at: **http://localhost:8000**

---

## 3. Frontend Setup

```bash
# Open new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: **http://localhost:5173**

---

## 4. Demo Accounts

### 📋 All Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| **Admin** | admin@dentalai.com | Admin123! |
| **Doctor** | doctor@dentalai.com | Doctor123! |
| **Receptionist** | reception@dentalai.com | Reception123! |
| **Patient** | patient@dentalai.com | Patient123! |

### 🎯 Patient Stories Included

1. **Alex Mercer** (alex.mercer@dentalai.com) - High-risk dropout (85% risk)
   - Missed multiple appointments
   - Low treatment progress (15%)
   - Queued intervention

2. **Sarah Connor** (sarah.connor@dentalai.com) - Successful intervention (25% risk)
   - Initially high-risk, responded to intervention
   - Now low-risk with good progress (75%)
   - Shows intervention effectiveness

3. **John Doe** (john.doe@dentalai.com) - Missed appointment today (55% risk)
   - Just missed root canal follow-up
   - Immediate intervention sent
   - Medium risk, needs attention

4. **Emily Chen** (emily.chen@dentalai.com) - Payment risk (65% risk)
   - Treatment 90% complete but payment overdue
   - Treatment on hold
   - Financial intervention sent

5. **Michael Scott** (michael.scott@dentalai.com) - Improving adherence (30% risk)
   - Initially missed appointments, now improving
   - Good clinical notes showing progress
   - Low risk, success story

---

## 5. Testing Workflows

### 🏥 Admin Dashboard
1. Login as `admin@dentalai.com`
2. View executive analytics
3. Check user management
4. Monitor AI workflows
5. View audit logs

### 👨‍⚕️ Doctor Dashboard
1. Login as `doctor@dentalai.com`
2. View patient risk overview
3. Check high-risk patients list
4. Navigate to patient details
5. Add clinical notes
6. Update treatment progress
7. Run AI predictions
8. View SHAP explanations

### 📋 Receptionist Dashboard
1. Login as `reception@dentalai.com`
2. View today's schedule
3. Mark patient attendance (Present/Absent)
4. Create new appointments
5. Manage schedule

### 😷 Patient Portal
1. Login as `patient@dentalai.com`
2. View upcoming appointments
3. Check treatment progress
4. View notifications
5. Book new appointments

### 🤖 AI Interventions
1. Login as `doctor@dentalai.com`
2. Navigate to "AI Insights" or "Interventions"
3. Select high-risk patient
4. Preview AI-generated message
5. Send intervention
6. View delivery status

---

## 6. Key Features to Demo

### Real-time Updates
- Mark attendance → Dashboard updates instantly
- Add clinical note → Appears in patient timeline
- Update treatment progress → Progress bar animates
- Send intervention → Appears in communication history

### AI Predictions
- Run prediction for any patient
- View probability and risk level
- Examine SHAP explanations
- See feature importance

### Analytics
- Admin dashboard shows live metrics
- Doctor analytics update with patient changes
- Appointment trends chart
- Risk distribution visualization

### Notifications
- Real-time notification badge updates
- Mark as read functionality
- Different notification types
- System alerts for high-risk patients

---

## 7. Troubleshooting

### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Restart database
docker-compose restart postgres

# Check database connection
psql postgresql://dentalai:dentalai_dev@localhost:5432/dentalai
```

### Migration Issues
```bash
# Reset migrations (if needed)
python manage.py migrate --fake-initial

# Or flush and re-seed
python manage.py flush --noinput
python manage.py seed_demo_data
```

### Frontend API Issues
```bash
# Check if backend is running
curl http://localhost:8000/api/v1/health/

# Should return: {"status": "ok", "service": "dentalai-api"}
```

### Clear Browser Cache
If frontend shows stale data:
- Hard refresh: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
- Clear localStorage: Open DevTools → Application → Local Storage → Clear

---

## 8. Demo Presentation Flow

### Suggested 5-Minute Demo

1. **Introduction** (30 seconds)
   - Login as Admin
   - Show executive dashboard with key metrics

2. **Doctor Workflow** (2 minutes)
   - Login as Doctor
   - Show patient risk overview
   - Click on high-risk patient (Alex Mercer)
   - Run AI prediction
   - Show SHAP explanation
   - Add clinical note
   - Update treatment progress

3. **AI Interventions** (1 minute)
   - Navigate to Interventions page
   - Select high-risk patient
   - Preview AI message
   - Send intervention
   - Show delivery tracking

4. **Receptionist Workflow** (1 minute)
   - Login as Receptionist
   - Show today's schedule
   - Mark patient as present
   - Create new appointment

5. **Patient Portal** (30 seconds)
   - Login as Patient
   - Show upcoming appointments
   - View treatment progress
   - Check notifications

### Screenshot Opportunities

1. **Admin Dashboard** - Executive overview with charts
2. **Doctor Dashboard** - Patient risk list with high-risk alerts
3. **Patient Detail** - Journey map, prediction history, SHAP explanation
4. **Interventions** - Message studio with preview
5. **Receptionist Dashboard** - Today's schedule with attendance
6. **Analytics Page** - Full executive analytics with all charts

---

## 9. API Testing

### Test Authentication
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "doctor@dentalai.com", "password": "Doctor123!"}'
```

### Test Patient List
```bash
curl http://localhost:8000/api/v1/patients/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Test AI Prediction
```bash
curl -X POST http://localhost:8000/api/v1/ai/predictions/generate/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"patient_id": "PATIENT_UUID"}'
```

---

## 10. Additional Commands

### View All Patients
```bash
python manage.py shell << EOF
from apps.patients.models import Patient
for p in Patient.objects.all():
    print(f"{p.user.email} - {p.user.full_name}")
EOF
```

### Check AI Model
```bash
python manage.py shell << EOF
from apps.ai_predictions.models import ModelVersion
model = ModelVersion.objects.filter(is_active=True).first()
if model:
    print(f"Active model: {model.name}")
    print(f"Metrics: {model.metrics}")
EOF
```

### View Statistics
```bash
python manage.py shell << EOF
from apps.users.models import User
from apps.patients.models import Patient
from apps.appointments.models import Appointment
from apps.ai_predictions.models import AIPrediction

print(f"Users: {User.objects.count()}")
print(f"Patients: {Patient.objects.count()}")
print(f"Appointments: {Appointment.objects.count()}")
print(f"Predictions: {AIPrediction.objects.count()}")
EOF
```

---

## 🎉 Ready to Demo!

Your DentalAI platform is now fully set up with:
- ✅ 9 users (4 demo accounts + 5 patient stories)
- ✅ 7 treatment types
- ✅ 25+ appointments with various statuses
- ✅ AI predictions with SHAP explanations
- ✅ Interventions with delivery tracking
- ✅ Notifications and alerts
- ✅ Complete analytics data

**Start presenting with confidence!** 🚀

---

## Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Review backend logs: `docker-compose logs postgres`
3. Check frontend console for errors
4. Verify database connection

For production deployment, see `docs/deployment.md`.