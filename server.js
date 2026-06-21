import express from 'express';
import pg from 'pg';

const app = express();
const { Pool } = pg;

const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  database: 'demo',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || 'postgres',
  ssl: false
});

app.use(express.json());
app.use(express.static('public'));

app.get('/api/metadata', async (req, res) => {
  try {
    const tokenRes = await fetch('http://169.254.169.254/latest/api/token', {
      method: 'PUT',
      headers: { 'X-aws-ec2-metadata-token-ttl-seconds': '21600' }
    });
    const token = await tokenRes.text();
    const [regionRes, instanceRes, azIdRes] = await Promise.all([
      fetch('http://169.254.169.254/latest/meta-data/placement/region', { headers: { 'X-aws-ec2-metadata-token': token } }),
      fetch('http://169.254.169.254/latest/meta-data/instance-id', { headers: { 'X-aws-ec2-metadata-token': token } }),
      fetch('http://169.254.169.254/latest/meta-data/placement/availability-zone-id', { headers: { 'X-aws-ec2-metadata-token': token } })
    ]);
    res.json({ region: await regionRes.text(), instanceId: await instanceRes.text(), azId: await azIdRes.text() });
  } catch (err) {
    res.json({ region: 'N/A', instanceId: 'N/A' });
  }
});

app.get('/api/products', async (req, res) => {
  try {
    const result = await pool.query('SELECT id, name, quantity AS qty FROM products ORDER BY id');
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/products', async (req, res) => {
  const { name, qty } = req.body;
  try {
    const result = await pool.query(
      'INSERT INTO products (name, quantity) VALUES ($1, $2) RETURNING id, name, quantity AS qty',
      [name, qty]
    );
    res.json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.put('/api/products/:id', async (req, res) => {
  const { name, qty } = req.body;
  try {
    const result = await pool.query(
      'UPDATE products SET name = $1, quantity = $2 WHERE id = $3 RETURNING id, name, quantity AS qty',
      [name, qty, req.params.id]
    );
    res.json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.delete('/api/products/:id', async (req, res) => {
  try {
    await pool.query('DELETE FROM products WHERE id = $1', [req.params.id]);
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, async () => {
  console.log(`Server running on port ${PORT}`);
  try {
    const result = await pool.query('SELECT NOW()');
    console.log('Database connected:', result.rows[0]);
  } catch (err) {
    console.error('Database connection failed:', err.message);
  }
});
