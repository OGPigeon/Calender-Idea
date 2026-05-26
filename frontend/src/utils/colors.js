export const EVENT_COLORS = {
  red: "#ff3b30",
  orange: "#ff9500",
  yellow: "#ffcc00",
  green: "#34c759",
  teal: "#5ac8fa",
  blue: "#007aff",
  purple: "#5856d6",
  pink: "#ff2d55",
  brown: "#a2845e",
};

export function getColor(evt) {
  return EVENT_COLORS[evt?.color] || EVENT_COLORS.blue;
}
