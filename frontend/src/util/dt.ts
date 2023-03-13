import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
require("dayjs/locale/de");
dayjs.extend(relativeTime);
dayjs.locale("de");

export function formatFromNow(now: Date | string, date: Date | string): string {
  return dayjs(date).from(now);
}
export function formatToDate(now: Date | string, date: Date | string) {
  return dayjs(now).to(date);
}
export function formatDateLong(date: Date | string) {
  return dayjs(date).format("YYYY-MM-DD HH:mm:ss [UTC]Z");
}
export function formatDateShort(now: Date, date: Date) {
  if (
    now.getFullYear() === date.getFullYear() &&
    now.getMonth() === date.getMonth() &&
    now.getDate() === date.getDate()
  ) {
    return dayjs(date).format("HH:mm:ss");
  }
  if (now.getFullYear() === date.getFullYear()) {
    return dayjs(date).format("D. MMM, HH:mm:ss");
  }
  return dayjs(date).format("YYYY-MM-DD HH:mm:ss");
}
export function isBefore(a: Date | string, b: Date | string) {
  return dayjs(a).isBefore(b);
}
export function isAfter(a: Date | string, b: Date | string) {
  return dayjs(a).isAfter(b);
}
