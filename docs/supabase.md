# Supabase Setup Guide

## Environment Variables

Ensure these variables are set in your `.env` file:

```env
SUPABASE_PASSWORD=your_database_password
SUPABASE_PROJECT_URL=https://your-project.supabase.co
SUPABASE_PUBLISHABLE_API_KEY=your_anon_public_key
SUPABASE_SECRET_API_KEY=your_service_role_key
```

---

## 1. Connecting to Supabase Client

### Python (Backend)

Install the Supabase Python client:

```bash
pip install supabase
```

Connect to Supabase:

```python
import os
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_PROJECT_URL")
key: str = os.environ.get("SUPABASE_SECRET_API_KEY")  # Use secret key for backend
supabase: Client = create_client(url, key)
```

### JavaScript/TypeScript (Frontend - Next.js)

Install the Supabase JS client:

```bash
npm install @supabase/supabase-js
```

Connect to Supabase:

```typescript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

---

## 2. Creating a Database Schema

You can create schemas directly in the Supabase Dashboard SQL Editor or using migrations.

### Example Schema (SQL)

```sql
-- Create a users table
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create a messages table
CREATE TABLE messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
```

---

## 3. Creating Migrations

### Using Supabase CLI

Install the Supabase CLI:

```bash
# Windows (scoop)
scoop install supabase

# macOS
brew install supabase/tap/supabase

# npm (cross-platform)
npm install -g supabase
```

Initialize and create migrations:

```bash
# Initialize Supabase in your project
supabase init

# Link to your remote project
supabase link --project-ref your-project-ref

# Create a new migration
supabase migration new create_users_table

# This creates a file in supabase/migrations/
# Edit the migration file with your SQL
```

Apply migrations:

```bash
# Apply to local database
supabase db reset

# Push to remote database
supabase db push
```

---

## 4. Adding Data to the Database

### Python

```python
# Insert a single row
data = supabase.table("users").insert({
    "email": "user@example.com",
    "name": "John Doe"
}).execute()

# Insert multiple rows
data = supabase.table("users").insert([
    {"email": "user1@example.com", "name": "User One"},
    {"email": "user2@example.com", "name": "User Two"}
]).execute()

# Query data
response = supabase.table("users").select("*").execute()
print(response.data)

# Update data
data = supabase.table("users").update({
    "name": "Updated Name"
}).eq("email", "user@example.com").execute()

# Delete data
data = supabase.table("users").delete().eq("email", "user@example.com").execute()
```

### JavaScript/TypeScript

```typescript
// Insert a single row
const { data, error } = await supabase
  .from('users')
  .insert({ email: 'user@example.com', name: 'John Doe' })

// Insert multiple rows
const { data, error } = await supabase
  .from('users')
  .insert([
    { email: 'user1@example.com', name: 'User One' },
    { email: 'user2@example.com', name: 'User Two' }
  ])

// Query data
const { data, error } = await supabase
  .from('users')
  .select('*')

// Update data
const { data, error } = await supabase
  .from('users')
  .update({ name: 'Updated Name' })
  .eq('email', 'user@example.com')

// Delete data
const { data, error } = await supabase
  .from('users')
  .delete()
  .eq('email', 'user@example.com')
```

---

## Quick Reference

| Task | Command/Method |
|------|----------------|
| Install CLI | `npm install -g supabase` |
| Init project | `supabase init` |
| New migration | `supabase migration new <name>` |
| Push migrations | `supabase db push` |
| Insert data | `.insert({...})` |
| Query data | `.select('*')` |
| Update data | `.update({...}).eq('col', 'val')` |
| Delete data | `.delete().eq('col', 'val')` |
