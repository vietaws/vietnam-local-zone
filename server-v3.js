import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();

app.use(express.static(path.join(__dirname, 'public'), {
  maxAge: '1h',
  etag: true,
  lastModified: true
}));

app.get('/api/metadata', async (req, res) => {
  try {
    const tokenRes = await fetch('http://169.254.169.254/latest/api/token', {
      method: 'PUT',
      headers: { 'X-aws-ec2-metadata-token-ttl-seconds': '21600' }
    });
    const token = await tokenRes.text();

    const [regionRes, instanceRes, azIdRes] = await Promise.all([
      fetch('http://169.254.169.254/latest/meta-data/placement/region', {
        headers: { 'X-aws-ec2-metadata-token': token }
      }),
      fetch('http://169.254.169.254/latest/meta-data/instance-id', {
        headers: { 'X-aws-ec2-metadata-token': token }
      }),
      fetch('http://169.254.169.254/latest/meta-data/placement/availability-zone-id', {
        headers: { 'X-aws-ec2-metadata-token': token }
      })
    ]);

    res.json({
      region: await regionRes.text(),
      instanceId: await instanceRes.text(),
      azId: await azIdRes.text()
    });
  } catch (err) {
    res.json({ region: 'N/A', instanceId: 'N/A', azId: 'N/A' });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
