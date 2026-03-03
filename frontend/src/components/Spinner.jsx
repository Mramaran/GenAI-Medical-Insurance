export default function Spinner({ size = 24 }) {
  return (
    <div
      style={{
        width: size,
        height: size,
        border: "3px solid #1e3a5f",
        borderTopColor: "#38BDF8",
        borderRadius: "50%",
        animation: "spin 0.8s linear infinite",
      }}
    />
  );
}
