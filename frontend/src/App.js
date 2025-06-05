import React, { useEffect, useState, useRef } from "react";

const API_BASE = "http://localhost:8000";

const goalIcons = {
  Home: "🏡",
  Retirement: "🏦",
  Education: "🎓",
};

function percent(current, goal) {
  if (!goal) return 0;
  return Math.round((current / goal) * 100);
}

function getProgressColor(p) {
  if (p >= 80) return "#22c55e"; // green
  if (p >= 50) return "#eab308"; // yellow
  return "#ef4444"; // red
}

function getInitials(name) {
  if (!name) return "?";
  const parts = name.split(" ");
  return (parts[0][0] + (parts[1]?.[0] || "")).toUpperCase();
}

function App() {
  const [clients, setClients] = useState([]);
  const [selectedClient, setSelectedClient] = useState("");
  const [goalHistory, setGoalHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [clientName, setClientName] = useState("");

  // Chatbot state
  const [chatOpen, setChatOpen] = useState(false);
  const [chatInput, setChatInput] = useState("");
  const [chatMessages, setChatMessages] = useState([
    { sender: "ai", text: "Hi! I'm your Advisor AI Assistant. How can I help you today?" }
  ]);
  const chatEndRef = useRef(null);

  useEffect(() => {
    fetch(`${API_BASE}/clients`)
      .then((res) => res.json())
      .then((data) => {
        setClients(data);
        if (selectedClient) {
          const found = data.find((c) => c.id === Number(selectedClient));
          setClientName(found ? found.client_name : "");
        }
      });
  }, []);

  useEffect(() => {
    if (selectedClient) {
      setLoading(true);
      fetch(`${API_BASE}/clients/${selectedClient}/all-goal-history`)
        .then((res) => res.json())
        .then((data) => {
          setGoalHistory(data);
          setLoading(false);
          const found = clients.find((c) => c.id === Number(selectedClient));
          setClientName(found ? found.client_name : "");
        });
    } else {
      setGoalHistory([]);
      setClientName("");
    }
  }, [selectedClient, clients]);

  useEffect(() => {
    if (chatOpen && chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [chatMessages, chatOpen]);

  function handleChatSend(e) {
    e.preventDefault();
    if (!chatInput.trim()) return;
    setChatMessages((msgs) => [
      ...msgs,
      { sender: "user", text: chatInput }
    ]);
    setChatInput("");
    // Placeholder: echo AI response after 1s
    setTimeout(() => {
      setChatMessages((msgs) => [
        ...msgs,
        { sender: "ai", text: "(AI will answer here in the next version!)" }
      ]);
    }, 1000);
  }

  return (
    <div style={{
      minHeight: "100vh",
      background: "#18181b",
      color: "#f3f4f6",
      maxWidth: 800,
      margin: "2rem auto",
      fontFamily: "'Inter', 'Roboto', sans-serif"
    }}>
      <h1 style={{ textAlign: "center", fontWeight: 700, fontSize: 36, marginBottom: 32, color: "#f3f4f6" }}>
        Client Goal History Viewer
      </h1>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 32 }}>
        {selectedClient && clientName && (
          <span style={{
            width: 40, height: 40, borderRadius: "50%", background: "#27272f", color: "#38bdf8", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700, fontSize: 20, marginRight: 16, border: "2px solid #38bdf8"
          }}>{getInitials(clientName)}</span>
        )}
        <label style={{ fontWeight: 500, fontSize: 18, marginRight: 12, color: "#e5e7eb" }}>
          Select Client:
        </label>
        <select
          value={selectedClient}
          onChange={(e) => setSelectedClient(e.target.value)}
          style={{ fontSize: 18, padding: "8px 16px", borderRadius: 8, border: "1px solid #333", minWidth: 220, background: "#23232a", color: "#f3f4f6" }}
        >
          <option value="">-- Choose a client --</option>
          {clients.map((c) => (
            <option key={c.id} value={c.id}>
              {c.client_name}
            </option>
          ))}
        </select>
      </div>
      {loading && <p style={{ textAlign: "center", color: "#a1a1aa" }}>Loading...</p>}
      {goalHistory.length > 0 && (
        <div style={{ marginTop: 16 }}>
          {goalHistory.map((goal) => {
            const prog = percent(goal.current_amount, goal.goal_amount);
            const onTrack = goal.on_track;
            const cardBorder = onTrack ? '#22c55e' : '#ef4444';
            const cardBg = onTrack ? '#1a2e1a' : '#2e1a1a';
            const progColor = onTrack ? '#22c55e' : '#ef4444';
            return (
              <div
                key={goal.id}
                style={{
                  marginBottom: 32,
                  border: `2px solid ${cardBorder}`,
                  borderRadius: 16,
                  padding: 24,
                  background: cardBg,
                  boxShadow: '0 2px 8px 0 rgba(0,0,0,0.10)',
                  transition: 'box-shadow 0.2s, border 0.2s',
                  cursor: 'pointer',
                }}
                onMouseEnter={e => {
                  e.currentTarget.style.boxShadow = `0 4px 16px 0 ${cardBorder}33`;
                  e.currentTarget.style.border = `2.5px solid ${cardBorder}`;
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.boxShadow = '0 2px 8px 0 rgba(0,0,0,0.10)';
                  e.currentTarget.style.border = `2px solid ${cardBorder}`;
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
                  <span style={{ fontSize: 32, marginRight: 12 }}>{goalIcons[goal.goal_type] || '🎯'}</span>
                  <h2 style={{ margin: 0, fontWeight: 700, fontSize: 26, color: '#f3f4f6', display: 'flex', alignItems: 'center' }}>
                    {goal.goal_type} Goal
                    <span style={{
                      marginLeft: 16,
                      padding: '2px 14px',
                      borderRadius: 12,
                      fontWeight: 700,
                      fontSize: 16,
                      background: onTrack ? '#22c55e' : '#ef4444',
                      color: '#fff',
                      display: 'inline-block',
                      verticalAlign: 'middle',
                      letterSpacing: 1
                    }}>
                      {onTrack ? '🟢 On Track' : '🔴 Off Track'}
                    </span>
                  </h2>
                </div>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: '8px 32px',
                  fontSize: 18,
                  marginBottom: 8,
                  color: '#e5e7eb',
                  fontWeight: 500
                }}>
                  <div><b>Goal Amount:</b> ${Number(goal.goal_amount).toLocaleString()}</div>
                  <div><b>Initial Amount:</b> ${Number(goal.initial_amount).toLocaleString()}</div>
                  <div><b>Current Amount:</b> ${Number(goal.current_amount).toLocaleString()}</div>
                  <div><b>Monthly Contribution:</b> ${Number(goal.monthly_contribution).toLocaleString()}</div>
                  <div><b>Withdrawal Period:</b> {goal.withdrawal_period_months} months</div>
                  <div><b>Expected Return Rate:</b> {(Number(goal.expected_return_rate) * 100).toFixed(2)}% per year</div>
                </div>
                <div style={{ margin: "16px 0 24px 0", height: 16, background: "#27272f", borderRadius: 8, position: "relative", overflow: "hidden" }}>
                  <div
                    style={{
                      width: prog + "%",
                      background: progColor,
                      height: "100%",
                      borderRadius: 8,
                      transition: "width 1s cubic-bezier(.4,2,.6,1)",
                    }}
                  ></div>
                  <span style={{ position: "absolute", right: 12, top: 0, fontWeight: 600, color: progColor }}>
                    {prog}%
                  </span>
                </div>
                <table style={{ width: "100%", borderCollapse: "collapse", background: "#18181b", borderRadius: 8, overflow: "hidden" }}>
                  <thead>
                    <tr style={{ background: "#23232a" }}>
                      <th style={{ borderBottom: "1px solid #27272f", padding: 8, fontWeight: 600, color: "#f3f4f6" }}>Date</th>
                      <th style={{ borderBottom: "1px solid #27272f", padding: 8, fontWeight: 600, color: "#f3f4f6" }}>Goal Amount</th>
                      <th style={{ borderBottom: "1px solid #27272f", padding: 8, fontWeight: 600, color: "#f3f4f6" }}>Current Amount</th>
                      <th style={{ borderBottom: "1px solid #27272f", padding: 8, fontWeight: 600, color: "#f3f4f6" }}>Message</th>
                    </tr>
                  </thead>
                  <tbody>
                    {goal.history.map((h, i) => (
                      <tr
                        key={i}
                        style={{
                          borderBottom: "1px solid #23232a",
                          background: i % 2 === 0 ? "#23232a" : "#1e1e23",
                          transition: "background 0.2s",
                          cursor: "pointer"
                        }}
                        onMouseEnter={e => e.currentTarget.style.background = "#2dd4bf33"}
                        onMouseLeave={e => e.currentTarget.style.background = i % 2 === 0 ? "#23232a" : "#1e1e23"}
                      >
                        <td style={{ padding: 8, color: "#e5e7eb" }}>{new Date(h.created_at).toLocaleDateString()}</td>
                        <td style={{ padding: 8, color: "#e5e7eb" }}>{Number(h.goal_amount).toLocaleString()}</td>
                        <td style={{ padding: 8, color: "#e5e7eb" }}>{Number(h.current_amount).toLocaleString()}</td>
                        <td style={{ padding: 8, color: "#f3f4f6" }}>{h.last_message_sent}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            );
          })}
        </div>
      )}

      {/* Chatbot Floating Button and Popup */}
      <button
        onClick={() => setChatOpen((v) => !v)}
        style={{
          position: "fixed",
          bottom: 32,
          right: 32,
          zIndex: 1000,
          background: chatOpen ? "#38bdf8" : "#23232a",
          color: chatOpen ? "#18181b" : "#38bdf8",
          border: "none",
          borderRadius: "50%",
          width: 60,
          height: 60,
          boxShadow: "0 2px 8px 0 rgba(0,0,0,0.20)",
          fontSize: 32,
          cursor: "pointer",
          transition: "background 0.2s, color 0.2s"
        }}
        aria-label="Open Advisor AI Assistant"
      >
        {chatOpen ? "✖️" : "🤖"}
      </button>
      {chatOpen && (
        <div
          style={{
            position: "fixed",
            bottom: 110,
            right: 32,
            width: 340,
            maxHeight: 480,
            background: "#23232a",
            color: "#f3f4f6",
            borderRadius: 16,
            boxShadow: "0 4px 24px 0 rgba(0,0,0,0.25)",
            display: "flex",
            flexDirection: "column",
            zIndex: 1001,
            overflow: "hidden"
          }}
        >
          <div style={{ padding: 16, borderBottom: "1px solid #27272f", fontWeight: 700, fontSize: 18, background: "#18181b" }}>
            Advisor AI Assistant
          </div>
          <div style={{ flex: 1, overflowY: "auto", padding: 16, fontSize: 15 }}>
            {chatMessages.map((msg, i) => (
              <div key={i} style={{ marginBottom: 12, display: "flex", justifyContent: msg.sender === "user" ? "flex-end" : "flex-start" }}>
                <div style={{
                  background: msg.sender === "user" ? "#38bdf8" : "#27272f",
                  color: msg.sender === "user" ? "#18181b" : "#f3f4f6",
                  borderRadius: 12,
                  padding: "8px 14px",
                  maxWidth: "80%",
                  fontWeight: 500,
                  boxShadow: msg.sender === "user" ? "0 1px 4px #38bdf822" : "none"
                }}>
                  {msg.text}
                </div>
              </div>
            ))}
            <div ref={chatEndRef} />
          </div>
          <form onSubmit={handleChatSend} style={{ display: "flex", borderTop: "1px solid #27272f", background: "#23232a" }}>
            <input
              type="text"
              value={chatInput}
              onChange={e => setChatInput(e.target.value)}
              placeholder="Type your question..."
              style={{
                flex: 1,
                padding: 12,
                border: "none",
                outline: "none",
                background: "#18181b",
                color: "#f3f4f6",
                fontSize: 15,
                borderRadius: 0
              }}
            />
            <button
              type="submit"
              style={{
                background: "#38bdf8",
                color: "#18181b",
                border: "none",
                padding: "0 18px",
                fontWeight: 700,
                fontSize: 18,
                cursor: "pointer"
              }}
              aria-label="Send"
            >
              ➤
            </button>
          </form>
        </div>
      )}
    </div>
  );
}

export default App; 