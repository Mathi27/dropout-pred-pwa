import { isAxiosError } from "axios";

type ApiErrorBody = Record<string, unknown> & {
  detail?: string | string[];
  non_field_errors?: string[];
};

function toMessages(value: unknown): string[] {
  if (typeof value === "string") return [value];
  if (Array.isArray(value)) {
    return value.flatMap((item) => toMessages(item));
  }
  if (value && typeof value === "object" && "string" in value) {
    return [String((value as { string: string }).string)];
  }
  return [];
}

/** Parse DRF validation errors into a user message and per-field strings. */
export function extractApiErrors(error: unknown): {
  message: string;
  fieldErrors: Record<string, string>;
} {
  if (!isAxiosError(error) || !error.response?.data) {
    return { message: "Something went wrong. Please try again.", fieldErrors: {} };
  }

  const data = error.response.data as ApiErrorBody;
  const fieldErrors: Record<string, string> = {};
  const messages: string[] = [];

  messages.push(...toMessages(data.detail));
  messages.push(...toMessages(data.non_field_errors));

  for (const [key, value] of Object.entries(data)) {
    if (key === "detail" || key === "non_field_errors") continue;
    const fieldMessages = toMessages(value);
    if (fieldMessages.length > 0) {
      fieldErrors[key] = fieldMessages.join(" ");
      messages.push(fieldMessages.join(" "));
    }
  }

  return {
    message: messages.filter(Boolean).join(" ") || "Request failed. Please check your input.",
    fieldErrors,
  };
}
