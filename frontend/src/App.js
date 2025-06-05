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
    <div style={{ minHeight: "100vh", background: "#f7fafd" }}>
      {/* Header Bar */}
      <header style={{
        width: "100%",
        background: "#fff",
        borderBottom: "1px solid #e5e7eb",
        boxShadow: "0 2px 8px 0 rgba(56,189,248,0.08)",
        height: 72,
        display: "flex",
        alignItems: "center",
        padding: "0 32px",
        position: "fixed",
        top: 0,
        left: 0,
        zIndex: 100
      }}>
        <img src="/images/aviso-logo.png" alt="Aviso Logo" style={{ height: 40, marginRight: 24 }} />
      </header>
      {/* Main Content */}
      <div style={{
        maxWidth: 900,
        margin: "72px auto 0 auto",
        background: "#fff",
        borderRadius: 18,
        boxShadow: "0 8px 32px 0 rgba(56,189,248,0.10)",
        padding: 36,
        minHeight: 600
      }}>
        <h1 style={{ textAlign: "center", fontWeight: 700, fontSize: 36, marginBottom: 32, color: "#22223b" }}>
          Goal Pulse
        </h1>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 32 }}>
          {selectedClient && clientName && (
            <span style={{
              width: 40, height: 40, borderRadius: "50%", background: "#e5e7eb", color: "#38bdf8", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700, fontSize: 20, marginRight: 16, border: "2px solid #38bdf8"
            }}>{getInitials(clientName)}</span>
          )}
          <label style={{ fontWeight: 500, fontSize: 18, marginRight: 12, color: "#22223b" }}>
            Select Client:
          </label>
          <select
            value={selectedClient}
            onChange={(e) => setSelectedClient(e.target.value)}
            style={{ fontSize: 18, padding: "8px 16px", borderRadius: 8, border: "1px solid #b6c6e3", minWidth: 220, background: "#f7fafd", color: "#22223b" }}
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
              const cardBg = onTrack ? '#e6f9f0' : '#fbeaea';
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
                    boxShadow: '0 2px 8px 0 rgba(56,189,248,0.08)',
                    transition: 'box-shadow 0.2s, border 0.2s',
                    cursor: 'pointer',
                  }}
                  onMouseEnter={e => {
                    e.currentTarget.style.boxShadow = `0 4px 16px 0 ${cardBorder}33`;
                    e.currentTarget.style.border = `2.5px solid ${cardBorder}`;
                  }}
                  onMouseLeave={e => {
                    e.currentTarget.style.boxShadow = '0 2px 8px 0 rgba(56,189,248,0.08)';
                    e.currentTarget.style.border = `2px solid ${cardBorder}`;
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
                    <span style={{ fontSize: 32, marginRight: 12 }}>{goalIcons[goal.goal_type] || '🎯'}</span>
                    <h2 style={{ margin: 0, fontWeight: 700, fontSize: 26, color: '#22223b', display: 'flex', alignItems: 'center' }}>
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
                    color: '#22223b',
                    fontWeight: 500
                  }}>
                    <div><b>Goal Amount:</b> ${Number(goal.goal_amount).toLocaleString()}</div>
                    <div><b>Initial Amount:</b> ${Number(goal.initial_amount).toLocaleString()}</div>
                    <div><b>Current Amount:</b> ${Number(goal.current_amount).toLocaleString()}</div>
                    <div><b>Monthly Contribution:</b> ${Number(goal.monthly_contribution).toLocaleString()}</div>
                    <div><b>Withdrawal Period:</b> {goal.withdrawal_period_months} months</div>
                    <div><b>Expected Return Rate:</b> {(Number(goal.expected_return_rate) * 100).toFixed(2)}% per year</div>
                  </div>
                  <div style={{ margin: "16px 0 24px 0", height: 16, background: "#e5e7eb", borderRadius: 8, position: "relative", overflow: "hidden" }}>
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
                  <table style={{ width: "100%", borderCollapse: "collapse", background: "#f7fafd", borderRadius: 8, overflow: "hidden" }}>
                    <thead>
                      <tr style={{ background: "#e5e7eb" }}>
                        <th style={{ borderBottom: "1px solid #b6c6e3", padding: 8, fontWeight: 600, color: "#22223b" }}>Date</th>
                        <th style={{ borderBottom: "1px solid #b6c6e3", padding: 8, fontWeight: 600, color: "#22223b" }}>Goal Amount</th>
                        <th style={{ borderBottom: "1px solid #b6c6e3", padding: 8, fontWeight: 600, color: "#22223b" }}>Current Amount</th>
                        <th style={{ borderBottom: "1px solid #b6c6e3", padding: 8, fontWeight: 600, color: "#22223b" }}>Message</th>
                      </tr>
                    </thead>
                    <tbody>
                      {goal.history.map((h, i) => (
                        <tr
                          key={i}
                          style={{
                            borderBottom: "1px solid #e5e7eb",
                            background: i % 2 === 0 ? "#f7fafd" : "#e5e7eb",
                            transition: "background 0.2s",
                            cursor: "pointer"
                          }}
                          onMouseEnter={e => e.currentTarget.style.background = "#bae6fd55"}
                          onMouseLeave={e => e.currentTarget.style.background = i % 2 === 0 ? "#f7fafd" : "#e5e7eb"}
                        >
                          <td style={{ padding: 8, color: "#22223b" }}>{new Date(h.created_at).toLocaleDateString()}</td>
                          <td style={{ padding: 8, color: "#22223b" }}>{Number(h.goal_amount).toLocaleString()}</td>
                          <td style={{ padding: 8, color: "#22223b" }}>{Number(h.current_amount).toLocaleString()}</td>
                          <td style={{ padding: 8, color: "#22223b" }}>{h.last_message_sent}</td>
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
    </div>
  );
}

export default App; 