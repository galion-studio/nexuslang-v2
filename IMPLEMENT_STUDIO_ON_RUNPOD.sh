#!/bin/bash
# Complete galion-studio implementation for RunPod
# Run this on your RunPod instance

cd /workspace/project-nexus/galion-studio

# Create package.json
cat > package.json << 'EOF'
{
  "name": "galion-studio",
  "version": "1.0.0",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  }
}
EOF

# Create pages directory
mkdir -p pages pages/generate

# Landing page
cat > pages/index.js << 'EOF'
export default function Home() {
  return (
    <div style={{minHeight:'100vh',background:'linear-gradient(135deg,#667eea,#764ba2)',padding:'50px',color:'white',fontFamily:'sans-serif'}}>
      <h1 style={{fontSize:'48px',marginBottom:'20px'}}>🎨 Galion Studio</h1>
      <p style={{fontSize:'20px',marginBottom:'40px'}}>AI-Powered Content Creation Platform</p>
      <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(250px,1fr))',gap:'20px'}}>
        <a href="/generate/image" style={{padding:'30px',background:'rgba(255,255,255,0.2)',borderRadius:'15px',textDecoration:'none',color:'white'}}>
          <div style={{fontSize:'48px'}}>🎨</div>
          <h3>Image Generation</h3>
          <p>DALL-E, Stable Diffusion</p>
        </a>
        <a href="/generate/video" style={{padding:'30px',background:'rgba(255,255,255,0.2)',borderRadius:'15px',textDecoration:'none',color:'white'}}>
          <div style={{fontSize:'48px'}}>🎬</div>
          <h3>Video Generation</h3>
          <p>Text-to-video, Image animation</p>
        </a>
        <a href="/generate/text" style={{padding:'30px',background:'rgba(255,255,255,0.2)',borderRadius:'15px',textDecoration:'none',color:'white'}}>
          <div style={{fontSize:'48px'}}>📝</div>
          <h3>Text Generation</h3>
          <p>Articles, stories, code</p>
        </a>
        <a href="/projects" style={{padding:'30px',background:'rgba(255,255,255,0.2)',borderRadius:'15px',textDecoration:'none',color:'white'}}>
          <div style={{fontSize:'48px'}}>📂</div>
          <h3>Projects</h3>
          <p>Manage your work</p>
        </a>
      </div>
    </div>
  )
}
EOF

# Image generation page
cat > pages/generate/image.js << 'EOF'
import {useState} from 'react'
export default function ImageGen() {
  const [prompt,setPrompt]=useState('')
  const [url,setUrl]=useState('')
  const [loading,setLoading]=useState(false)
  const generate=async()=>{
    setLoading(true)
    try{
      const res=await fetch('/api/v2/ai/image',{
        method:'POST',
        headers:{'Content-Type':'application/json','Authorization':`Bearer ${localStorage.getItem('token')}`},
        body:JSON.stringify({prompt,model:'dall-e-3'})
      })
      const data=await res.json()
      setUrl(data.url)
    }catch(e){alert(e.message)}
    setLoading(false)
  }
  return (
    <div style={{minHeight:'100vh',background:'#f5f5f5',padding:'50px'}}>
      <h1>🎨 Image Generation</h1>
      <textarea value={prompt} onChange={e=>setPrompt(e.target.value)} placeholder="Describe your image..." style={{width:'100%',height:'100px',padding:'15px',marginBottom:'20px',fontSize:'16px',borderRadius:'8px',border:'1px solid #ddd'}}/>
      <button onClick={generate} disabled={loading} style={{padding:'15px 30px',background:'#667eea',color:'white',border:'none',borderRadius:'8px',fontSize:'18px',cursor:'pointer'}}>{loading?'Generating...':'Generate Image'}</button>
      {url&&<img src={url} style={{marginTop:'30px',maxWidth:'100%',borderRadius:'15px',boxShadow:'0 10px 30px rgba(0,0,0,0.2)'}}/>}
    </div>
  )
}
EOF

# Video generation page
cat > pages/generate/video.js << 'EOF'
import {useState} from 'react'
export default function VideoGen() {
  const [prompt,setPrompt]=useState('')
  const [url,setUrl]=useState('')
  const [loading,setLoading]=useState(false)
  const generate=async()=>{
    setLoading(true)
    try{
      const res=await fetch('/api/v2/video/generate',{
        method:'POST',
        headers:{'Content-Type':'application/json','Authorization':`Bearer ${localStorage.getItem('token')}`},
        body:JSON.stringify({prompt,duration:4})
      })
      const data=await res.json()
      setUrl(data.video_url)
    }catch(e){alert(e.message)}
    setLoading(false)
  }
  return (
    <div style={{minHeight:'100vh',background:'#f5f5f5',padding:'50px'}}>
      <h1>🎬 Video Generation</h1>
      <textarea value={prompt} onChange={e=>setPrompt(e.target.value)} placeholder="Describe your video..." style={{width:'100%',height:'100px',padding:'15px',marginBottom:'20px',fontSize:'16px',borderRadius:'8px',border:'1px solid #ddd'}}/>
      <button onClick={generate} disabled={loading} style={{padding:'15px 30px',background:'#667eea',color:'white',border:'none',borderRadius:'8px',fontSize:'18px',cursor:'pointer'}}>{loading?'Generating...':'Generate Video'}</button>
      {url&&<video src={url} controls style={{marginTop:'30px',maxWidth:'100%',borderRadius:'15px',boxShadow:'0 10px 30px rgba(0,0,0,0.2)'}}/>}
    </div>
  )
}
EOF

# Text generation page
cat > pages/generate/text.js << 'EOF'
import {useState} from 'react'
export default function TextGen() {
  const [prompt,setPrompt]=useState('')
  const [text,setText]=useState('')
  const [loading,setLoading]=useState(false)
  const generate=async()=>{
    setLoading(true)
    try{
      const res=await fetch('/api/v2/ai/chat',{
        method:'POST',
        headers:{'Content-Type':'application/json','Authorization':`Bearer ${localStorage.getItem('token')}`},
        body:JSON.stringify({messages:[{role:'user',content:prompt}],max_tokens:1000})
      })
      const data=await res.json()
      setText(data.content)
    }catch(e){alert(e.message)}
    setLoading(false)
  }
  return (
    <div style={{minHeight:'100vh',background:'#f5f5f5',padding:'50px'}}>
      <h1>📝 Text Generation</h1>
      <textarea value={prompt} onChange={e=>setPrompt(e.target.value)} placeholder="What do you want to generate?" style={{width:'100%',height:'100px',padding:'15px',marginBottom:'20px',fontSize:'16px',borderRadius:'8px',border:'1px solid #ddd'}}/>
      <button onClick={generate} disabled={loading} style={{padding:'15px 30px',background:'#667eea',color:'white',border:'none',borderRadius:'8px',fontSize:'18px',cursor:'pointer'}}>{loading?'Generating...':'Generate Text'}</button>
      {text&&<pre style={{marginTop:'30px',padding:'20px',background:'white',borderRadius:'8px',whiteSpace:'pre-wrap'}}>{text}</pre>}
    </div>
  )
}
EOF

# Projects page
cat > pages/projects.js << 'EOF'
import {useState,useEffect} from 'react'
export default function Projects() {
  const [projects,setProjects]=useState([])
  useEffect(()=>{
    fetch('/api/v2/projects/',{headers:{'Authorization':`Bearer ${localStorage.getItem('token')}`}})
      .then(r=>r.json())
      .then(d=>setProjects(d.projects||[]))
  },[])
  return (
    <div style={{minHeight:'100vh',background:'#f5f5f5',padding:'50px'}}>
      <h1>📂 Projects</h1>
      <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(300px,1fr))',gap:'20px',marginTop:'30px'}}>
        {projects.map(p=>(
          <div key={p.id} style={{padding:'20px',background:'white',borderRadius:'10px',boxShadow:'0 2px 10px rgba(0,0,0,0.1)'}}>
            <h3>{p.name}</h3>
            <p>{p.description}</p>
            <small>{new Date(p.updated_at).toLocaleDateString()}</small>
          </div>
        ))}
      </div>
    </div>
  )
}
EOF

# Install and start
npm install
nohup npm run dev -- --port 3001 > /workspace/logs/studio.log 2>&1 &

echo "✅ Galion Studio implemented and started on port 3001!"
echo "URL: https://galion-studio-1762994724.loca.lt"
echo "Password: 213.173.105.83"

