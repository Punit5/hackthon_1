CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    client_name VARCHAR(100) NOT NULL,
    age INTEGER
);

CREATE TABLE goals (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    goal_type VARCHAR(50) NOT NULL,
    goal_amount NUMERIC NOT NULL,
    initial_amount NUMERIC NOT NULL,
    current_amount NUMERIC NOT NULL,
    monthly_contribution NUMERIC DEFAULT 0,
    withdrawal_period_months INTEGER DEFAULT 0,
    expected_return_rate NUMERIC DEFAULT 0.05
);

CREATE TABLE goal_history (
    id SERIAL PRIMARY KEY,
    goal_id INTEGER REFERENCES goals(id),
    goal_amount NUMERIC NOT NULL,
    current_amount NUMERIC NOT NULL,
    last_message_sent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed clients
INSERT INTO clients (client_name, age) VALUES
('Jane Doe', 45),
('John Smith', 38),
('Alice Lee', 29);

-- Seed goals
INSERT INTO goals (client_id, goal_type, goal_amount, initial_amount, current_amount, monthly_contribution, withdrawal_period_months, expected_return_rate) VALUES
(1, 'Retirement', 100000, 72000, 82000, 1000, 60, 0.06),
(1, 'Home', 50000, 10000, 20000, 500, 36, 0.05),
(2, 'Home', 50000, 20000, 25000, 400, 24, 0.05),
(3, 'Education', 30000, 10000, 15000, 300, 48, 0.04);

-- Seed goal history
-- Jane Doe Retirement (goal_id=1)
INSERT INTO goal_history (goal_id, goal_amount, current_amount, last_message_sent, created_at) VALUES
(1, 100000, 72000, 'Hi Jane 👋, you''re at 72% of your retirement goal! 🔥 Keep going strong! - Dave', '2024-01-01 10:00:00'),
(1, 100000, 74000, 'Hi Jane 👋, you''re at 74% of your retirement goal! 💪 Keep it up! - Dave', '2024-02-01 10:00:00'),
(1, 100000, 76000, 'Hi Jane 👋, you''re at 76% of your retirement goal! - Dave 🚀', '2024-03-01 10:00:00'),
(1, 100000, 78000, 'Hi Jane 👋, you''re at 78% of your retirement goal! - Dave 🌟', '2024-04-01 10:00:00'),
(1, 100000, 80000, 'Hi Jane 👋, you''re at 80% of your retirement goal! - Dave 🎉', '2024-05-01 10:00:00'),
(1, 100000, 82000, 'Hi Jane 👋, you''re at 82% of your retirement goal! Amazing progress! - Dave 🚀', '2024-06-01 10:00:00');

-- Jane Doe Home (goal_id=2)
INSERT INTO goal_history (goal_id, goal_amount, current_amount, last_message_sent, created_at) VALUES
(2, 50000, 10000, 'Hi Jane 👋, you''re at 20% of your home goal! 🏡 Keep saving! - Dave 🌟', '2024-01-01 10:00:00'),
(2, 50000, 12000, 'Hi Jane 👋, you''re at 24% of your home goal! - Dave 🏡', '2024-02-01 10:00:00'),
(2, 50000, 14000, 'Hi Jane 👋, you''re at 28% of your home goal! - Dave 🚀 🏡', '2024-03-01 10:00:00'),
(2, 50000, 16000, 'Hi Jane 👋, you''re at 32% of your home goal! - Dave 🌟 🏡', '2024-04-01 10:00:00'),
(2, 50000, 18000, 'Hi Jane 👋, you''re at 36% of your home goal! - Dave 💪 🏡', '2024-05-01 10:00:00'),
(2, 50000, 20000, 'Hi Jane 👋, you''re at 40% of your home goal! Keep saving! - Dave 🌟 🏡', '2024-06-01 10:00:00');

-- John Smith Home (goal_id=3)
INSERT INTO goal_history (goal_id, goal_amount, current_amount, last_message_sent, created_at) VALUES
(3, 50000, 20000, 'Hi John 👋, you''re at 40% of your home goal! Keep saving! - Dave 🏡', '2024-01-01 10:00:00'),
(3, 50000, 21000, 'Hi John 👋, you''re at 42% of your home goal! - Dave 🏡', '2024-02-01 10:00:00'),
(3, 50000, 22000, 'Hi John 👋, you''re at 44% of your home goal! - Dave 💪 🏡', '2024-03-01 10:00:00'),
(3, 50000, 23000, 'Hi John 👋, you''re at 46% of your home goal! - Dave 🏡', '2024-04-01 10:00:00'),
(3, 50000, 24000, 'Hi John 👋, you''re at 48% of your home goal! Keep saving! - Dave 🌟 🏡', '2024-05-01 10:00:00'),
(3, 50000, 25000, 'Hi John 👋, you''re at 50% of your home goal! Keep saving! - Dave 🏡', '2024-06-01 10:00:00');

-- Alice Lee Education (goal_id=4)
INSERT INTO goal_history (goal_id, goal_amount, current_amount, last_message_sent, created_at) VALUES
(4, 30000, 10000, 'Hi Alice 👋, you''re at 33% of your education goal! Stay focused! - Dave 📚', '2024-01-01 10:00:00'),
(4, 30000, 11000, 'Hi Alice 👋, you''re at 37% of your education goal! - Dave 📚', '2024-02-01 10:00:00'),
(4, 30000, 12000, 'Hi Alice 👋, you''re at 40% of your education goal! - Dave 💪 📚', '2024-03-01 10:00:00'),
(4, 30000, 13000, 'Hi Alice 👋, you''re at 43% of your education goal! - Dave 📚', '2024-04-01 10:00:00'),
(4, 30000, 14000, 'Hi Alice 👋, you''re at 47% of your education goal! - Dave 🎉 📚', '2024-05-01 10:00:00'),
(4, 30000, 15000, 'Hi Alice 👋, you''re at 50% of your education goal! Stay focused! - Dave 🎉 📚', '2024-06-01 10:00:00'); 