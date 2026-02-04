import React from "react";
import { clsx } from "clsx";
import { AlertTriangle, Phone } from "lucide-react";

export interface EmergencyAlertProps {
  message?: string;
  showPhone?: boolean;
  className?: string;
}

export const EmergencyAlert: React.FC<EmergencyAlertProps> = ({
  message = "如果您正在经历紧急症状，请立即拨打 120 急救电话！",
  showPhone = true,
  className,
}) => {
  return (
    <div
      className={clsx(
        "bg-gradient-to-r from-red-500 to-rose-500 text-white rounded-xl p-4 shadow-lg",
        className,
      )}
      role="alert"
    >
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center flex-shrink-0">
          <AlertTriangle className="w-6 h-6" />
        </div>
        <div className="flex-1">
          <h4 className="font-bold text-lg">⚠️ 紧急提醒</h4>
          <p className="text-sm text-white/90 mt-1">{message}</p>
        </div>
      </div>

      {showPhone && (
        <a
          href="tel:120"
          className="mt-4 flex items-center justify-center gap-2 w-full py-3 bg-white text-red-600 font-bold rounded-lg hover:bg-white/90 transition-colors"
        >
          <Phone className="w-5 h-5" />
          拨打 120
        </a>
      )}
    </div>
  );
};

EmergencyAlert.displayName = "EmergencyAlert";
