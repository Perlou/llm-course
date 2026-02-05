/**
 * MediMind - 提醒管理页面
 *
 * 慢病管理提醒的创建、编辑、删除功能。
 */

import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Card, Button } from "@medimind/ui";
import {
  reminderApi,
  Reminder,
  ReminderType,
  RepeatType,
} from "@medimind/api-client";

// 提醒类型配置
const REMINDER_TYPES: { value: ReminderType; label: string; icon: string }[] = [
  { value: "medication", label: "用药提醒", icon: "💊" },
  { value: "measurement", label: "测量提醒", icon: "📊" },
  { value: "checkup", label: "复查提醒", icon: "🏥" },
  { value: "other", label: "其他提醒", icon: "⏰" },
];

const REPEAT_TYPES: { value: RepeatType; label: string }[] = [
  { value: "once", label: "单次" },
  { value: "daily", label: "每天" },
  { value: "weekly", label: "每周" },
  { value: "monthly", label: "每月" },
];

const WEEKDAYS = ["一", "二", "三", "四", "五", "六", "日"];

export default function ReminderPage() {
  const navigate = useNavigate();
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingReminder, setEditingReminder] = useState<Reminder | null>(null);
  const [filterType, setFilterType] = useState<ReminderType | "">("");

  // 表单状态
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    reminder_type: "medication" as ReminderType,
    reminder_time: "08:00",
    repeat_type: "daily" as RepeatType,
    days_of_week: [1, 2, 3, 4, 5] as number[],
    day_of_month: 1,
  });

  // 加载提醒列表
  const loadReminders = useCallback(async () => {
    try {
      setLoading(true);
      const data = await reminderApi.getList(filterType || undefined);
      setReminders(data);
    } catch (err) {
      console.error("加载提醒失败:", err);
    } finally {
      setLoading(false);
    }
  }, [filterType]);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/login");
      return;
    }
    loadReminders();
  }, [navigate, loadReminders]);

  // 请求通知权限
  const requestNotificationPermission = async () => {
    if ("Notification" in window && Notification.permission === "default") {
      await Notification.requestPermission();
    }
  };

  useEffect(() => {
    requestNotificationPermission();
  }, []);

  // 打开创建弹窗
  const handleCreate = () => {
    setEditingReminder(null);
    setFormData({
      title: "",
      description: "",
      reminder_type: "medication",
      reminder_time: "08:00",
      repeat_type: "daily",
      days_of_week: [1, 2, 3, 4, 5],
      day_of_month: 1,
    });
    setShowModal(true);
  };

  // 打开编辑弹窗
  const handleEdit = (reminder: Reminder) => {
    setEditingReminder(reminder);
    setFormData({
      title: reminder.title,
      description: reminder.description || "",
      reminder_type: reminder.reminder_type,
      reminder_time: reminder.reminder_time,
      repeat_type: reminder.repeat_type,
      days_of_week: reminder.days_of_week || [1, 2, 3, 4, 5],
      day_of_month: reminder.day_of_month || 1,
    });
    setShowModal(true);
  };

  // 提交表单
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingReminder) {
        await reminderApi.update(editingReminder.id, formData);
      } else {
        await reminderApi.create(formData);
      }
      setShowModal(false);
      loadReminders();
    } catch (err) {
      console.error("保存提醒失败:", err);
    }
  };

  // 切换启用状态
  const handleToggle = async (id: string) => {
    try {
      await reminderApi.toggle(id);
      loadReminders();
    } catch (err) {
      console.error("切换提醒失败:", err);
    }
  };

  // 删除提醒
  const handleDelete = async (id: string) => {
    if (!window.confirm("确定要删除这个提醒吗？")) return;
    try {
      await reminderApi.remove(id);
      loadReminders();
    } catch (err) {
      console.error("删除提醒失败:", err);
    }
  };

  // 切换周几
  const toggleWeekday = (day: number) => {
    setFormData((prev) => ({
      ...prev,
      days_of_week: prev.days_of_week.includes(day)
        ? prev.days_of_week.filter((d) => d !== day)
        : [...prev.days_of_week, day].sort(),
    }));
  };

  // 获取提醒图标
  const getReminderIcon = (type: ReminderType) => {
    return REMINDER_TYPES.find((t) => t.value === type)?.icon || "⏰";
  };

  return (
    <div style={styles.container}>
      {/* 头部 */}
      <div style={styles.header}>
        <button style={styles.backButton} onClick={() => navigate("/")}>
          ← 返回
        </button>
        <h1 style={styles.title}>提醒管理</h1>
      </div>

      {/* 筛选和添加 */}
      <div style={styles.toolbar}>
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value as ReminderType | "")}
          style={styles.select}
        >
          <option value="">全部类型</option>
          {REMINDER_TYPES.map((type) => (
            <option key={type.value} value={type.value}>
              {type.icon} {type.label}
            </option>
          ))}
        </select>
        <Button onClick={handleCreate}>➕ 添加提醒</Button>
      </div>

      {/* 通知权限提示 */}
      {"Notification" in window && Notification.permission === "denied" && (
        <Card style={styles.warningCard}>
          ⚠️ 浏览器通知已被禁用，请在设置中开启以接收提醒通知。
        </Card>
      )}

      {/* 提醒列表 */}
      {loading ? (
        <div style={styles.loading}>加载中...</div>
      ) : reminders.length === 0 ? (
        <Card style={styles.emptyCard}>
          <div style={styles.emptyIcon}>⏰</div>
          <p>暂无提醒</p>
          <p style={styles.emptyHint}>点击上方"添加提醒"创建您的第一个提醒</p>
        </Card>
      ) : (
        <div style={styles.list}>
          {reminders.map((reminder) => (
            <Card key={reminder.id} style={styles.reminderCard}>
              <div style={styles.reminderHeader}>
                <span style={styles.reminderIcon}>
                  {getReminderIcon(reminder.reminder_type)}
                </span>
                <div style={styles.reminderInfo}>
                  <h3 style={styles.reminderTitle}>{reminder.title}</h3>
                  <p style={styles.reminderTime}>{reminder.reminder_time}</p>
                </div>
                <label style={styles.switch}>
                  <input
                    type="checkbox"
                    checked={reminder.is_enabled}
                    onChange={() => handleToggle(reminder.id)}
                  />
                  <span style={styles.slider}></span>
                </label>
              </div>
              {reminder.description && (
                <p style={styles.reminderDesc}>{reminder.description}</p>
              )}
              <div style={styles.reminderMeta}>
                <span style={styles.tag}>
                  {
                    REPEAT_TYPES.find((r) => r.value === reminder.repeat_type)
                      ?.label
                  }
                </span>
                {reminder.repeat_type === "weekly" && reminder.days_of_week && (
                  <span style={styles.weekdays}>
                    {reminder.days_of_week
                      .map((d) => `周${WEEKDAYS[d - 1]}`)
                      .join("、")}
                  </span>
                )}
              </div>
              <div style={styles.actions}>
                <button
                  style={styles.editBtn}
                  onClick={() => handleEdit(reminder)}
                >
                  编辑
                </button>
                <button
                  style={styles.deleteBtn}
                  onClick={() => handleDelete(reminder.id)}
                >
                  删除
                </button>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* 弹窗 */}
      {showModal && (
        <div style={styles.modalOverlay} onClick={() => setShowModal(false)}>
          <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
            <h2 style={styles.modalTitle}>
              {editingReminder ? "编辑提醒" : "添加提醒"}
            </h2>
            <form onSubmit={handleSubmit}>
              <div style={styles.formGroup}>
                <label style={styles.label}>标题</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) =>
                    setFormData((prev) => ({ ...prev, title: e.target.value }))
                  }
                  placeholder="如：服用降压药"
                  style={styles.input}
                  required
                />
              </div>

              <div style={styles.formGroup}>
                <label style={styles.label}>类型</label>
                <div style={styles.typeGrid}>
                  {REMINDER_TYPES.map((type) => (
                    <button
                      key={type.value}
                      type="button"
                      style={{
                        ...styles.typeBtn,
                        ...(formData.reminder_type === type.value
                          ? styles.typeBtnActive
                          : {}),
                      }}
                      onClick={() =>
                        setFormData((prev) => ({
                          ...prev,
                          reminder_type: type.value,
                        }))
                      }
                    >
                      <span>{type.icon}</span>
                      <span>{type.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              <div style={styles.formRow}>
                <div style={styles.formGroup}>
                  <label style={styles.label}>时间</label>
                  <input
                    type="time"
                    value={formData.reminder_time}
                    onChange={(e) =>
                      setFormData((prev) => ({
                        ...prev,
                        reminder_time: e.target.value,
                      }))
                    }
                    style={styles.input}
                    required
                  />
                </div>
                <div style={styles.formGroup}>
                  <label style={styles.label}>重复</label>
                  <select
                    value={formData.repeat_type}
                    onChange={(e) =>
                      setFormData((prev) => ({
                        ...prev,
                        repeat_type: e.target.value as RepeatType,
                      }))
                    }
                    style={styles.input}
                  >
                    {REPEAT_TYPES.map((type) => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {formData.repeat_type === "weekly" && (
                <div style={styles.formGroup}>
                  <label style={styles.label}>选择周几</label>
                  <div style={styles.weekdayGrid}>
                    {WEEKDAYS.map((day, index) => (
                      <button
                        key={index}
                        type="button"
                        style={{
                          ...styles.weekdayBtn,
                          ...(formData.days_of_week.includes(index + 1)
                            ? styles.weekdayBtnActive
                            : {}),
                        }}
                        onClick={() => toggleWeekday(index + 1)}
                      >
                        {day}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {formData.repeat_type === "monthly" && (
                <div style={styles.formGroup}>
                  <label style={styles.label}>每月几号</label>
                  <input
                    type="number"
                    min="1"
                    max="31"
                    value={formData.day_of_month}
                    onChange={(e) =>
                      setFormData((prev) => ({
                        ...prev,
                        day_of_month: parseInt(e.target.value),
                      }))
                    }
                    style={styles.input}
                  />
                </div>
              )}

              <div style={styles.formGroup}>
                <label style={styles.label}>描述（可选）</label>
                <textarea
                  value={formData.description}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      description: e.target.value,
                    }))
                  }
                  placeholder="如：每天早晚各一次，饭后服用"
                  style={styles.textarea}
                />
              </div>

              <div style={styles.modalActions}>
                <button
                  type="button"
                  style={styles.cancelBtn}
                  onClick={() => setShowModal(false)}
                >
                  取消
                </button>
                <button type="submit" style={styles.submitBtn}>
                  {editingReminder ? "保存" : "创建"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

// 样式
const styles: Record<string, React.CSSProperties> = {
  container: {
    maxWidth: 600,
    margin: "0 auto",
    padding: 20,
    minHeight: "100vh",
    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
  },
  header: {
    display: "flex",
    alignItems: "center",
    gap: 16,
    marginBottom: 24,
  },
  backButton: {
    background: "rgba(255,255,255,0.2)",
    border: "none",
    color: "#fff",
    padding: "8px 16px",
    borderRadius: 8,
    cursor: "pointer",
    fontSize: 14,
  },
  title: {
    color: "#fff",
    fontSize: 24,
    margin: 0,
  },
  toolbar: {
    display: "flex",
    gap: 12,
    marginBottom: 20,
  },
  select: {
    flex: 1,
    padding: "10px 12px",
    borderRadius: 8,
    border: "none",
    fontSize: 14,
    background: "#fff",
  },
  warningCard: {
    background: "#fff3cd",
    color: "#856404",
    padding: 12,
    marginBottom: 16,
  },
  loading: {
    color: "#fff",
    textAlign: "center",
    padding: 40,
  },
  emptyCard: {
    textAlign: "center",
    padding: 40,
  },
  emptyIcon: {
    fontSize: 48,
    marginBottom: 16,
  },
  emptyHint: {
    color: "#666",
    fontSize: 14,
  },
  list: {
    display: "flex",
    flexDirection: "column",
    gap: 12,
  },
  reminderCard: {
    padding: 16,
  },
  reminderHeader: {
    display: "flex",
    alignItems: "center",
    gap: 12,
  },
  reminderIcon: {
    fontSize: 32,
  },
  reminderInfo: {
    flex: 1,
  },
  reminderTitle: {
    margin: 0,
    fontSize: 16,
    fontWeight: 600,
  },
  reminderTime: {
    margin: 0,
    color: "#667eea",
    fontSize: 20,
    fontWeight: 700,
  },
  switch: {
    position: "relative",
    display: "inline-block",
    width: 50,
    height: 28,
  },
  slider: {
    position: "absolute",
    cursor: "pointer",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: "#ccc",
    transition: "0.4s",
    borderRadius: 28,
  },
  reminderDesc: {
    margin: "12px 0 0 44px",
    color: "#666",
    fontSize: 14,
  },
  reminderMeta: {
    marginTop: 12,
    marginLeft: 44,
    display: "flex",
    gap: 8,
    alignItems: "center",
  },
  tag: {
    background: "#e8e8ff",
    color: "#667eea",
    padding: "4px 8px",
    borderRadius: 4,
    fontSize: 12,
  },
  weekdays: {
    color: "#888",
    fontSize: 12,
  },
  actions: {
    marginTop: 12,
    marginLeft: 44,
    display: "flex",
    gap: 12,
  },
  editBtn: {
    background: "none",
    border: "1px solid #667eea",
    color: "#667eea",
    padding: "6px 16px",
    borderRadius: 6,
    cursor: "pointer",
  },
  deleteBtn: {
    background: "none",
    border: "1px solid #dc3545",
    color: "#dc3545",
    padding: "6px 16px",
    borderRadius: 6,
    cursor: "pointer",
  },
  modalOverlay: {
    position: "fixed",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: "rgba(0,0,0,0.5)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 1000,
  },
  modal: {
    background: "#fff",
    borderRadius: 16,
    padding: 24,
    width: "90%",
    maxWidth: 400,
    maxHeight: "90vh",
    overflow: "auto",
  },
  modalTitle: {
    margin: "0 0 20px 0",
    fontSize: 20,
  },
  formGroup: {
    marginBottom: 16,
  },
  formRow: {
    display: "flex",
    gap: 16,
  },
  label: {
    display: "block",
    marginBottom: 6,
    fontWeight: 500,
    color: "#333",
  },
  input: {
    width: "100%",
    padding: "10px 12px",
    border: "1px solid #ddd",
    borderRadius: 8,
    fontSize: 14,
    boxSizing: "border-box",
  },
  textarea: {
    width: "100%",
    padding: "10px 12px",
    border: "1px solid #ddd",
    borderRadius: 8,
    fontSize: 14,
    minHeight: 80,
    resize: "vertical",
    boxSizing: "border-box",
  },
  typeGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(2, 1fr)",
    gap: 8,
  },
  typeBtn: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: 4,
    padding: 12,
    border: "1px solid #ddd",
    borderRadius: 8,
    background: "#fff",
    cursor: "pointer",
  },
  typeBtnActive: {
    borderColor: "#667eea",
    background: "#f0f2ff",
  },
  weekdayGrid: {
    display: "flex",
    gap: 8,
  },
  weekdayBtn: {
    width: 36,
    height: 36,
    border: "1px solid #ddd",
    borderRadius: "50%",
    background: "#fff",
    cursor: "pointer",
  },
  weekdayBtnActive: {
    borderColor: "#667eea",
    background: "#667eea",
    color: "#fff",
  },
  modalActions: {
    display: "flex",
    gap: 12,
    marginTop: 24,
  },
  cancelBtn: {
    flex: 1,
    padding: "12px 20px",
    border: "1px solid #ddd",
    borderRadius: 8,
    background: "#fff",
    cursor: "pointer",
  },
  submitBtn: {
    flex: 1,
    padding: "12px 20px",
    border: "none",
    borderRadius: 8,
    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    color: "#fff",
    cursor: "pointer",
    fontWeight: 600,
  },
};
