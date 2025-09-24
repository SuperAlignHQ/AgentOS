import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const formatDate = (dateString: string) =>
  new Date(dateString).toLocaleDateString("en-US", {
    month: "short",
    day: "2-digit",
    year: "numeric",
  });

export const capitalizeFirstLetter = (str: string) => {
  if (!str) return str;
  return str.charAt(0).toUpperCase() + str.slice(1);
};

export const formatText = (text: string) => {
  if (!text) return text;
  // Split by underscore and capitalize each word
  return text
    .split("_")
    .map((word) => capitalizeFirstLetter(word))
    .join(" ");
};

export const FAIL = "fail"
export const PASS = "pass"
export const APPROVED = "approved"
export const DECLINED = "declined"
export const SUSPENDED = "suspended"
export const NEED_REVIEW = "need review"
export const NEW = "new"
export const REROUTED = "rerouted"
export const PENDING = "pending"
