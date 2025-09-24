import { APPROVED, cn, DECLINED, FAIL, NEED_REVIEW, NEW, PASS, PENDING, REROUTED, SUSPENDED } from "@/lib/utils";

interface StatusBadgeProps {
  status: string;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const getStatusStyles = (status: string) => {
    const normalizedStatus = status.toLowerCase();

    // Green statuses (Pass/Approved)
    if (
      normalizedStatus === PASS ||
      normalizedStatus === APPROVED ||
      normalizedStatus === "a1" ||
      normalizedStatus === "true"
    ) {
      return {
        backgroundColor: "#F0FDF4",
        borderColor: "#BBF7D0",
        textColor: "#166534",
      };
    }

    // Red statuses (Fail/Declined)
    if (
      normalizedStatus === FAIL ||
      normalizedStatus === DECLINED ||
      normalizedStatus === "false" ||
      normalizedStatus === "failed"
    ) {
      return {
        backgroundColor: "#FEF3F2",
        borderColor: "#FECDCA",
        textColor: "#DC2626",
      };
    }

    // Yellow statuses (Suspended/Need Review/New/Rerouted/Pending)
    if (
      normalizedStatus === SUSPENDED ||
      normalizedStatus === NEED_REVIEW ||
      normalizedStatus === NEW ||
      normalizedStatus === REROUTED ||
      normalizedStatus === PENDING
    ) {
      return {
        backgroundColor: "#FEFBE8",
        borderColor: "#FEEE95",
        textColor: "#CA8A04",
      };
    }

    // Default gray for unknown statuses
    return {
      backgroundColor: "#F9FAFB",
      borderColor: "#E5E7EB",
      textColor: "#374151",
    };
  };

  const styles = getStatusStyles(status);

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-md border px-2 py-1 text-center font-normal text-xs leading-relaxed"
      )}
      style={{
        backgroundColor: styles.backgroundColor,
        borderColor: styles.borderColor,
        color: styles.textColor,
      }}
    >
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
}
