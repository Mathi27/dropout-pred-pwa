export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface Patient {
  id: string;
  full_name: string;
  email: string;
  date_of_birth?: string;
  gender?: string;
  address?: string;
  risk_score?: number;
  risk_level?: string | null;
  created_at: string;
}

export interface Appointment {
  id: string;
  patient: string;
  patient_detail?: Patient;
  doctor?: string;
  doctor_detail?: { id: string; full_name: string };
  scheduled_at: string;
  duration_minutes: number;
  status: string;
  attendance: string;
  reason?: string;
  notes?: string;
}

export interface Notification {
  id: string;
  title: string;
  body: string;
  notification_type: string;
  is_read: boolean;
  created_at: string;
}

export interface PatientTreatment {
  id: string;
  status: string;
  progress_percent: number;
  treatment_detail?: { name: string };
  started_at?: string;
}

export interface Payment {
  id: string;
  amount: string;
  status: string;
  payment_date: string;
  method: string;
  description?: string;
}

export interface ClinicalNote {
  id: string;
  patient: string;
  content: string;
  visit_date: string;
}

export interface AuditLog {
  id: string;
  action: string;
  resource_type: string;
  resource_id: string;
  actor_detail?: { email: string; full_name: string };
  created_at: string;
}

export interface AdminAnalytics {
  kpis: Record<string, number>;
  appointment_trends: { date: string; scheduled: number; completed: number }[];
  notification_metrics: { total: number; unread: number; read: number };
  attendance_heatmap: { date: string; present: number; absent: number; pending: number }[];
  adherence_kpis?: {
    attendance_rate: number;
    miss_rate: number;
    treatment_completion_rate: number;
    payment_on_time_rate: number;
    notification_read_rate: number;
  };
  dropout_metrics?: {
    high_risk_share: number;
    previous_high_risk_share: number;
    share_delta: number;
    current_total: number;
    previous_total: number;
  };
  intervention_success?: {
    messages_sent: number;
    delivery_success_rate: number;
    retry_rate: number;
    impact: { improved: number; worsened: number; stable: number };
  };
  communication_effectiveness?: {
    notification_read_rate: number;
    notification_by_type: { notification_type: string; count: number }[];
  };
  treatment_funnel?: {
    total: number;
    active: number;
    on_hold: number;
    completed: number;
    cancelled: number;
  };
  risk_segmentation?: { low: number; medium: number; high: number };
  cohort_comparison?: { category: string; low: number; medium: number; high: number }[];
  doctor_performance?: {
    doctor_id: string;
    doctor_name: string;
    appointments_total: number;
    appointments_completed: number;
    completion_rate: number;
    patients_seen: number;
    high_risk_patients: number;
  }[];
}

export interface ModelVersion {
  id: string;
  name: string;
  model_type: string;
  trained_at: string;
  metrics?: Record<string, number>;
  calibration?: Record<string, unknown>;
  feature_names?: string[];
  hyperparameters?: Record<string, unknown>;
  data_summary?: Record<string, unknown>;
}

export interface AIPrediction {
  id: string;
  patient: string;
  patient_detail?: Patient;
  probability: number;
  risk_score?: number;
  risk_level: string;
  features?: Record<string, number>;
  model_version?: ModelVersion;
  prediction_source?: string;
  created_at: string;
}

export interface ShapExplanation {
  id: string;
  prediction_id: string;
  base_value: number;
  shap_values: Record<string, number>;
  top_features: { feature: string; value: number; impact: number }[];
  feature_values: Record<string, number>;
  created_at: string;
}

export interface ModelMetrics {
  model_version: ModelVersion;
  metrics: Record<string, number>;
  calibration?: Record<string, unknown>;
}

export interface RiskTrendPoint {
  date: string;
  low: number;
  medium: number;
  high: number;
  total: number;
}

export interface AIGeneratedMessage {
  id: string;
  patient: string;
  patient_detail?: Patient;
  prediction?: string;
  created_by?: string;
  message_type: string;
  language: string;
  prompt: string;
  content: string;
  template_key?: string;
  provider?: string;
  confidence_score: number;
  risk_level?: string;
  risk_score?: number | null;
  delivery_status: string;
  personalization?: Record<string, string>;
  metadata?: Record<string, unknown>;
  deliveries?: DeliveryTracking[];
  created_at: string;
}

export interface DeliveryTracking {
  id: string;
  status: string;
  channel: string;
  attempt: number;
  last_attempt_at?: string | null;
  delivered_at?: string | null;
  language?: string;
  error_message?: string;
  metadata?: Record<string, unknown>;
  created_at: string;
}

export interface InterventionLog {
  id: string;
  patient: string;
  message?: string | null;
  actor?: string | null;
  action: string;
  status: string;
  impact_score?: number | null;
  notes?: string;
  metadata?: Record<string, unknown>;
  created_at: string;
}

export interface InterventionMetrics {
  totals: { messages: number; delivered: number; failed: number };
  status_counts: { status: string; count: number }[];
  language_counts: { language: string; count: number }[];
  message_type_counts: { message_type: string; count: number }[];
  avg_confidence: number;
}

export interface AIAnalyticsOverview {
  risk_distribution: { low: number; medium: number; high: number };
  confidence_distribution: { low: number; medium: number; high: number };
  risk_trends: { rising: number; falling: number; stable: number };
  completion_trend: { week: string; avg_progress: number }[];
  adherence_heatmap: { weekday: number; present: number; absent: number; pending: number }[];
  notification_effectiveness: Record<string, { sent: number; read: number; read_rate: number }>;
  intervention_impact: { improved: number; worsened: number; stable: number };
  segmentation: { category: string; low: number; medium: number; high: number }[];
}

export interface PatientTimelineEvent {
  type: string;
  timestamp: string;
  status?: string;
  attendance?: string;
  risk_level?: string;
  probability?: number;
  amount?: number;
  notification_type?: string;
}
