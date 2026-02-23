export default function AttendanceCard({ image }) {
  return (
    <div className="attendance-card">
      <div className="image-container">
        <img
          src={image}
          alt="Captured Photo"
          className="main-img"
        />
      </div>

      <div className="card-info">
        <div className="card-title">Kareru</div>

        <div className="creator-row">
          <div className="creator-icon">S</div>
          <span>Student</span>
        </div>

        <div className="stats-box">
          <h3>Attendance Verified</h3>
        </div>
      </div>
    </div>
  );
}