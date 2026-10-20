
import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Film,
  Clapperboard,
  FileText,
  LayoutDashboard,
  Settings,
  Play,
  Download,
  LoaderCircle,
  CheckCircle2,
  AlertCircle,
  Clock3,
  Sparkles,
  RefreshCw,
  Trash2,
  Monitor,
  Smartphone,
  Square,
  Activity,
  Volume2,
} from "lucide-react";
import "./styles.css";

const API = "";

const formats = [
  { id: "landscape", label: "Landscape", ratio: "16:9", icon: Monitor },
  { id: "portrait", label: "Portrait", ratio: "9:16", icon: Smartphone },
  { id: "square", label: "Square", ratio: "1:1", icon: Square },
];

const styles = [
  { value: "cinematic", label: "Cinematic" },
  { value: "documentary", label: "Documentary" },
  { value: "social_media", label: "Social media" },
  { value: "educational", label: "Educational" },
];

const sampleScript =
  "Every great idea starts with a simple question. What if we could turn our imagination into something real? With creativity, technology, and the courage to begin, ordinary moments can become extraordinary stories.";

function getJob(data) {
  return data?.job || data?.data?.job || data?.data || data;
}

function getJobId(job) {
  return job?.job_id || job?.id || job?.jobId;
}

function getStatus(job) {
  return String(job?.status || "queued").toLowerCase();
}

function getProgress(job) {
  const value = Number(job?.progress ?? job?.progress_percent ?? 0);
  return Math.max(0, Math.min(100, value));
}

function isCompleted(status) {
  return ["completed", "complete", "succeeded", "success", "done"].includes(
    status
  );
}

function isFailed(status) {
  return ["failed", "error", "cancelled", "canceled"].includes(status);
}

function readableError(detail, status) {
  if (typeof detail === "string") return detail;

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        const location = Array.isArray(item.loc)
          ? item.loc.join(" → ")
          : "";
        return `${location ? `${location}: ` : ""}${item.msg || JSON.stringify(item)}`;
      })
      .join("\n");
  }

  if (detail && typeof detail === "object") {
    return JSON.stringify(detail, null, 2);
  }

  return `Request failed (HTTP ${status})`;
}

async function apiRequest(path, options = {}) {
  let response;

  try {
    response = await fetch(`${API}${path}`, options);
  } catch {
    throw new Error(
      "Could not reach the backend. Check that FastAPI is running on port 8000."
    );
  }

  const text = await response.text();
  let data = {};

  try {
    data = text ? JSON.parse(text) : {};
  } catch {
    data = { detail: text };
  }

  if (!response.ok) {
    throw new Error(
      readableError(data?.detail ?? data?.message ?? data, response.status)
    );
  }

  return data;
}

function App() {
  const [script, setScript] = useState("");
  const [format, setFormat] = useState("landscape");
  const [style, setStyle] = useState("cinematic");
  const [job, setJob] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [busy, setBusy] = useState(false);
  const [backend, setBackend] = useState("checking");
  const [error, setError] = useState("");
  const [audioFile, setAudioFile] = useState(null);
  const [audioResult, setAudioResult] = useState(null);
  const [audioBusy, setAudioBusy] = useState(false);
  const [audioError, setAudioError] = useState("");
  const pollRef = useRef(null);

  const currentStatus = job ? getStatus(job) : "";
  const completed = isCompleted(currentStatus);
  const failed = isFailed(currentStatus);
  const progress = job ? getProgress(job) : 0;
  const jobId = job ? getJobId(job) : null;

  async function checkBackend() {
    try {
      await apiRequest("/health");
      setBackend("online");
    } catch {
      setBackend("offline");
    }
  }

  async function loadJobs() {
    try {
      const data = await apiRequest("/api/v1/jobs?limit=6");
      const list = Array.isArray(data)
        ? data
        : data?.jobs || data?.items || data?.data?.jobs || [];
      setJobs(Array.isArray(list) ? list : []);
    } catch {
      // Recent jobs are optional.
    }
  }

  useEffect(() => {
    checkBackend();
    loadJobs();

    const timer = setInterval(checkBackend, 10000);

    return () => {
      clearInterval(timer);
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

  useEffect(() => {
    if (!jobId || completed || failed) {
      if (pollRef.current) {
        clearInterval(pollRef.current);
        pollRef.current = null;
      }
      setBusy(false);
      return;
    }

    let active = true;

    async function refreshJob() {
      try {
        const data = await apiRequest(
          `/api/v1/jobs/${encodeURIComponent(jobId)}`
        );
        if (active) setJob(getJob(data));
      } catch (err) {
        if (active) {
          setError(`Unable to refresh job status: ${err.message}`);
        }
      }
    }

    refreshJob();
    pollRef.current = setInterval(refreshJob, 2000);

    return () => {
      active = false;
      if (pollRef.current) {
        clearInterval(pollRef.current);
        pollRef.current = null;
      }
    };
  }, [jobId, completed, failed]);

  useEffect(() => {
    if (completed || failed) {
      setBusy(false);
      loadJobs();
    }
  }, [completed, failed]);

  async function createVideo(event) {
    event.preventDefault();
    setError("");

    if (!script.trim()) {
      setError("Please enter your script before creating a video.");
      return;
    }

    if (backend !== "online") {
      setError("Backend is not connected. Check the FastAPI server first.");
      return;
    }

    setBusy(true);
    setJob(null);

    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }

    const selectedFormat =
      formats.find((item) => item.id === format)?.ratio || "16:9";

    const payload = {
      script: script.trim(),
      aspect_ratio: selectedFormat,
      style,
    };

    try {
      const data = await apiRequest("/api/v1/jobs", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Idempotency-Key":
            globalThis.crypto?.randomUUID?.() ||
            `${Date.now()}-${Math.random()}`,
        },
        body: JSON.stringify(payload),
      });

      const newJob = getJob(data);
      const newJobId = getJobId(newJob);

      if (!newJobId) {
        throw new Error(
          `The API returned no job ID. Response: ${JSON.stringify(data, null, 2)}`
        );
      }

      setJob(newJob);
      loadJobs();
    } catch (err) {
      setError(err.message || "Could not create the video job.");
      setBusy(false);
    }
  }

  async function analyzeAudio(event) {
    event.preventDefault();
    setAudioError("");
    setAudioResult(null);

    if (!audioFile) {
      setAudioError("Choose a WAV audio file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", audioFile);
    setAudioBusy(true);

    try {
      const data = await apiRequest("/api/v1/audio/analyze", {
        method: "POST",
        body: formData,
      });
      setAudioResult(data);
    } catch (err) {
      setAudioError(err.message);
    } finally {
      setAudioBusy(false);
    }
  }

  function openVideo(id) {
    if (!id) return;

    window.open(
      `${API}/api/v1/jobs/${encodeURIComponent(id)}/video`,
      "_blank",
      "noopener,noreferrer"
    );
  }

  function resetWorkspace() {
    setScript("");
    setJob(null);
    setError("");
    setBusy(false);

    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }

  function restoreJob(item) {
    setJob(item);
    setError("");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  // Accept the response shape returned by the current audio endpoint.
  const audioAnalysis = audioResult?.analysis || null;
  const silenceIntervals = Array.isArray(audioAnalysis?.silence_intervals)
    ? audioAnalysis.silence_intervals
    : [];

  function formatSilenceInterval(interval) {
    if (typeof interval !== "object" || interval === null) {
      return String(interval);
    }

    const start =
      interval.start_seconds ?? interval.start ?? interval.start_time;
    const end = interval.end_seconds ?? interval.end ?? interval.end_time;

    if (start !== undefined && end !== undefined) {
      return `${Number(start).toFixed(2)}s – ${Number(end).toFixed(2)}s`;
    }

    return JSON.stringify(interval);
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#workspace" aria-label="IncuBrix Studio home">
          <div className="brand-mark">
            <Clapperboard size={23} strokeWidth={2.1} />
          </div>
          <div>
            <div className="brand-name">Shiva Creates</div>
            <div className="brand-subtitle">INCUBRIX STUDIO</div>
          </div>
        </a>

        <div className="side-label">WORKSPACE</div>
        <nav className="side-nav">
          <a className="nav-link active" href="#workspace">
            <LayoutDashboard size={18} /> Dashboard
          </a>
          <a className="nav-link" href="#recent">
            <Film size={18} /> My videos
          </a>
          <a className="nav-link" href="#audio">
            <Volume2 size={18} /> Audio tools
          </a>
        </nav>

        <div className="sidebar-bottom">
          <div className="backend-card">
            <div className="backend-card-heading">
              <Activity size={16} />
              <span>Backend status</span>
            </div>
            <div className="backend-status">
              <span className={`status-dot ${backend}`} />
              {backend === "online"
                ? "Connected"
                : backend === "offline"
                  ? "Not connected"
                  : "Checking connection"}
            </div>
            <button className="subtle-button" onClick={checkBackend}>
              <RefreshCw size={13} /> Check connection
            </button>
          </div>

          <div className="sidebar-footer">
            <Sparkles size={15} />
            <span>Turn ideas into stories.</span>
          </div>
        </div>
      </aside>

      <main className="main-area" id="workspace">
        <header className="topbar">
          <div className="breadcrumb">
            Workspace <span>/</span> <strong>Video creator</strong>
          </div>
          <div className="topbar-right">
            <span className="live-indicator">
              <span className={`status-dot ${backend}`} />
              {backend === "online" ? "API online" : "API status"}
            </span>
            <div className="avatar">IB</div>
          </div>
        </header>

        <div className="page-content">
          <section className="welcome-row">
            <div>
              <div className="eyebrow">
                <Sparkles size={14} /> SCRIPT TO VIDEO ENGINE
              </div>
              <h1>Bring your story to life.</h1>
              <p className="welcome-copy">
                Your script is the starting point. Let IncuBrix turn it into a
                video with visuals, voiceover, and a story worth watching.
              </p>
            </div>
            <div className="welcome-decoration">
              <div className="decoration-circle circle-one" />
              <div className="decoration-circle circle-two" />
              <Film size={48} strokeWidth={1.2} />
            </div>
          </section>

          <div className="workspace-grid">
            <section className="panel editor-panel">
              <div className="panel-heading">
                <div className="panel-title-group">
                  <div className="panel-icon">
                    <FileText size={19} />
                  </div>
                  <div>
                    <h2>Create a video</h2>
                    <p>Start with a script. We'll handle the pipeline.</p>
                  </div>
                </div>
                <span className="step-pill">STEP 01</span>
              </div>

              <form onSubmit={createVideo}>
                <div className="field-heading">
                  <label htmlFor="script">Your script</label>
                  <span className="field-hint">
                    {script.trim() ? script.trim().split(/\s+/).length : 0}{" "}
                    words · {script.length} characters
                  </span>
                </div>

                <textarea
                  id="script"
                  className="script-input"
                  placeholder="Paste your script here... Tell your story, explain an idea, or write your next video."
                  value={script}
                  onChange={(event) => setScript(event.target.value)}
                  rows={8}
                  required
                />

                <div className="text-actions">
                  <button
                    className="text-button"
                    type="button"
                    onClick={() => setScript(sampleScript)}
                  >
                    <Sparkles size={14} /> Use sample script
                  </button>
                  <button
                    className="text-button muted"
                    type="button"
                    onClick={resetWorkspace}
                  >
                    <Trash2 size={14} /> Clear
                  </button>
                </div>

                <div className="section-divider" />

                <div className="field-heading">
                  <label>Video format</label>
                  <span className="field-hint">Choose your canvas</span>
                </div>

                <div className="format-grid">
                  {formats.map((item) => {
                    const Icon = item.icon;
                    return (
                      <button
                        key={item.id}
                        type="button"
                        className={`format-card ${format === item.id ? "selected" : ""}`}
                        onClick={() => setFormat(item.id)}
                        aria-pressed={format === item.id}
                      >
                        <Icon size={22} />
                        <span className="format-label">{item.label}</span>
                        <span className="format-ratio">{item.ratio}</span>
                        {format === item.id && (
                          <CheckCircle2 className="format-check" size={16} />
                        )}
                      </button>
                    );
                  })}
                </div>

                <div className="section-divider" />

                <div className="field-heading">
                  <label htmlFor="style">Creative direction</label>
                  <span className="field-hint">Set the mood</span>
                </div>

                <select
                  id="style"
                  className="select-input"
                  value={style}
                  onChange={(event) => setStyle(event.target.value)}
                >
                  {styles.map((item) => (
                    <option key={item.value} value={item.value}>
                      {item.label}
                    </option>
                  ))}
                </select>

                {error && (
                  <div className="alert error-alert" role="alert">
                    <AlertCircle size={17} />
                    <pre className="error-text">{error}</pre>
                  </div>
                )}

                <button
                  className="primary-button create-button"
                  type="submit"
                  disabled={busy || !script.trim()}
                >
                  {busy ? (
                    <LoaderCircle className="spin" size={18} />
                  ) : (
                    <Play size={17} fill="currentColor" />
                  )}
                  {busy ? "Creating your video..." : "Generate video"}
                  {!busy && <span className="button-arrow">→</span>}
                </button>

                <p className="privacy-note">
                  <Settings size={13} /> Your video is generated by your
                  connected IncuBrix backend.
                </p>
              </form>
            </section>

            <section className="panel preview-panel">
              <div className="panel-heading">
                <div className="panel-title-group">
                  <div className="panel-icon preview-icon">
                    <Film size={19} />
                  </div>
                  <div>
                    <h2>Video preview</h2>
                    <p>Your latest generation</p>
                  </div>
                </div>
                {completed && <span className="success-pill">READY</span>}
              </div>

              <div className={`video-stage stage-${format}`}>
                {completed && jobId ? (
                  <video
                    className="video-player"
                    controls
                    preload="metadata"
                    src={`${API}/api/v1/jobs/${encodeURIComponent(jobId)}/video`}
                  >
                    Your browser does not support video playback.
                  </video>
                ) : (
                  <div className="empty-preview">
                    <div className="preview-art">
                      <div className="art-ring ring-one" />
                      <div className="art-ring ring-two" />
                      <div className="art-center">
                        <Play size={25} fill="currentColor" />
                      </div>
                    </div>
                    <h3>
                      {failed
                        ? "Generation needs attention"
                        : busy
                          ? "Your story is in production"
                          : "Your next story starts here"}
                    </h3>
                    <p>
                      {failed
                        ? String(job?.error || job?.message || "The job failed.")
                        : busy
                          ? String(job?.message || "Preparing visuals and assembling your video.")
                          : "Your generated video will appear here when it's ready."}
                    </p>
                  </div>
                )}
              </div>

              {job && (
                <div className="job-details">
                  <div className="job-detail-top">
                    <div>
                      <span className="mini-label">JOB STATUS</span>
                      <div className="job-status-text">
                        {failed ? (
                          <AlertCircle size={15} />
                        ) : completed ? (
                          <CheckCircle2 size={15} />
                        ) : (
                          <LoaderCircle className="spin" size={15} />
                        )}
                        {currentStatus.replace(/_/g, " ")}
                      </div>
                    </div>
                    <div className="progress-number">{progress}%</div>
                  </div>

                  <div className="progress-track">
                    <div
                      className={`progress-fill ${failed ? "failed-fill" : ""}`}
                      style={{ width: `${progress}%` }}
                    />
                  </div>

                  <p className="job-message">
                    {String(
                      job.message ||
                        job?.result?.message ||
                        (completed
                          ? "Your video is ready."
                          : "Waiting for the next pipeline update.")
                    )}
                  </p>

                  {completed && (
                    <button
                      className="primary-button download-button"
                      onClick={() => openVideo(jobId)}
                    >
                      <Download size={17} /> Open or download MP4
                    </button>
                  )}

                  {failed && (
                    <button
                      className="secondary-button"
                      onClick={() => {
                        setJob(null);
                        setError("");
                      }}
                    >
                      <RefreshCw size={15} /> Dismiss and try again
                    </button>
                  )}
                </div>
              )}

              {!job && (
                <div className="preview-tip">
                  <div className="tip-icon">
                    <Sparkles size={17} />
                  </div>
                  <div>
                    <strong>A little inspiration</strong>
                    <p>
                      Try a short script first. You can experiment with
                      different formats and creative directions.
                    </p>
                  </div>
                </div>
              )}

              <div className="preview-meta">
                <div>
                  <span className="mini-label">FORMAT</span>
                  <strong>
                    {formats.find((item) => item.id === format)?.ratio}
                  </strong>
                </div>
                <div>
                  <span className="mini-label">STYLE</span>
                  <strong>
                    {styles.find((item) => item.value === style)?.label}
                  </strong>
                </div>
                <div>
                  <span className="mini-label">ENGINE</span>
                  <strong>IncuBrix API</strong>
                </div>
              </div>
            </section>
          </div>

          <section className="panel recent-panel" id="recent">
            <div className="panel-heading recent-heading">
              <div className="panel-title-group">
                <div className="panel-icon">
                  <Clock3 size={19} />
                </div>
                <div>
                  <h2>Recent jobs</h2>
                  <p>Jobs returned by your backend</p>
                </div>
              </div>
              <button className="text-button" type="button" onClick={loadJobs}>
                <RefreshCw size={14} /> Refresh
              </button>
            </div>

            {jobs.length > 0 ? (
              <div className="recent-list">
                {jobs.map((item, index) => {
                  const id = getJobId(item);
                  const status = getStatus(item);
                  return (
                    <button
                      className="recent-item"
                      key={id || index}
                      type="button"
                      onClick={() => restoreJob(item)}
                    >
                      <div className="recent-file-icon">
                        <Film size={18} />
                      </div>
                      <div className="recent-info">
                        <strong>
                          {item.title ||
                            item.script?.slice?.(0, 48) ||
                            `Video job ${String(id || index + 1).slice(0, 12)}`}
                        </strong>
                        <span>{id || "Job ID unavailable"}</span>
                      </div>
                      <span
                        className={`job-badge ${
                          isCompleted(status)
                            ? "badge-complete"
                            : isFailed(status)
                              ? "badge-failed"
                              : "badge-pending"
                        }`}
                      >
                        {status.replace(/_/g, " ")}
                      </span>
                    </button>
                  );
                })}
              </div>
            ) : (
              <div className="empty-recent">
                <Film size={23} />
                <p>No recent jobs to show yet.</p>
                <span>Create a video and it may appear here.</span>
              </div>
            )}
          </section>

          <section className="panel audio-panel" id="audio">
            <div className="panel-heading">
              <div className="panel-title-group">
                <div className="panel-icon audio-icon">
                  <Volume2 size={19} />
                </div>
                <div>
                  <h2>Audio analysis</h2>
                  <p>WAV duration and silence detection</p>
                </div>
              </div>
              <span className="step-pill">OPTIONAL</span>
            </div>

            <form className="audio-form" onSubmit={analyzeAudio}>
              <label className="upload-area" htmlFor="audio-file">
                <Volume2 size={22} />
                <strong>
                  {audioFile ? audioFile.name : "Choose a WAV audio file"}
                </strong>
                <span>Click to browse your computer</span>
                <input
                  id="audio-file"
                  type="file"
                  accept=".wav,audio/wav,audio/x-wav"
                  onChange={(event) => {
                    setAudioFile(event.target.files?.[0] || null);
                    setAudioResult(null);
                    setAudioError("");
                  }}
                />
              </label>

              <button
                className="secondary-button"
                type="submit"
                disabled={audioBusy || !audioFile}
              >
                {audioBusy ? (
                  <LoaderCircle className="spin" size={16} />
                ) : (
                  <Activity size={16} />
                )}
                {audioBusy ? "Analyzing audio..." : "Analyze audio"}
              </button>
            </form>

            {audioError && (
              <div className="alert error-alert" role="alert">
                <AlertCircle size={17} />
                <pre className="error-text">{audioError}</pre>
              </div>
            )}

            {audioResult && audioAnalysis && (
              <div className="audio-results">
                <div className="audio-results-heading">
                  <div>
                    <span className="mini-label">ANALYSIS COMPLETE</span>
                    <h3>Your audio report</h3>
                  </div>
                  <CheckCircle2 size={23} />
                </div>

                <div className="audio-result-grid">
                  <div className="audio-result-card">
                    <span>Audio duration</span>
                    <strong>
                      {Number(audioAnalysis.duration_seconds).toFixed(2)} sec
                    </strong>
                    <small>Total length of your WAV file</small>
                  </div>

                  <div className="audio-result-card">
                    <span>Silence intervals</span>
                    <strong>{silenceIntervals.length}</strong>
                    <small>
                      {silenceIntervals.length === 0
                        ? "No silence intervals reported"
                        : "Possible pauses detected"}
                    </small>
                  </div>

                  <div className="audio-result-card">
                    <span>Analysis status</span>
                    <strong>{audioResult.status || "Complete"}</strong>
                    <small>Backend response received</small>
                  </div>
                </div>

                <div className="audio-file-detail">
                  <FileText size={17} />
                  <div>
                    <span>Analyzed file</span>
                    <strong>
                      {audioAnalysis.filename || audioFile?.name || "WAV audio"}
                    </strong>
                  </div>
                </div>

                {silenceIntervals.length > 0 && (
                  <div className="silence-list">
                    <h4>Detected silence intervals</h4>
                    <ul>
                      {silenceIntervals.map((interval, index) => (
                        <li key={index}>
                          <Clock3 size={15} />
                          {formatSilenceInterval(interval)}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {silenceIntervals.length === 0 && (
                  <p className="audio-note">
                    <CheckCircle2 size={16} />
                    The backend reported no silence intervals for this file.
                  </p>
                )}
              </div>
            )}

            {audioResult && !audioAnalysis && (
              <div className="audio-results">
                <h3>Audio response received</h3>
                <p>
                  The backend returned data, but it did not include an
                  <code> analysis </code> object.
                </p>
                <pre className="json-result">
                  {JSON.stringify(audioResult, null, 2)}
                </pre>
              </div>
            )}
          </section>

          <footer className="page-footer">
            <span>IncuBrix Studio</span>
            <span>Script and Voiceover to B-roll Video Engine</span>
          </footer>
        </div>
      </main>
    </div>
  );
}

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
