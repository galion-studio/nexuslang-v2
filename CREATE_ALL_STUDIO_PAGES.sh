#!/bin/bash
# Create ALL galion.studio pages on RunPod
# Run this in /workspace/project-nexus/galion-studio

cd /workspace/project-nexus/galion-studio

echo "🎨 Creating all galion.studio pages..."

# Create directories
mkdir -p pages/generate pages/api

# 1. Enhanced Landing Page
cat > pages/index.js << 'EOF'
import {useRouter} from 'next/router'
export default function Home(){
const router=useRouter()
return(
<div style={{minHeight:'100vh',background:'linear-gradient(135deg,#667eea,#764ba2)',color:'white',fontFamily:'sans-serif'}}>
<div style={{padding:'50px',maxWidth:'1200px',margin:'0 auto'}}>
<h1 style={{fontSize:'64px',fontWeight:'800',marginBottom:'20px'}}>🎨 Galion Studio</h1>
<p style={{fontSize:'28px',marginBottom:'50px',opacity:0.9}}>AI-Powered Content Creation</p>
<div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(250px,1fr))',gap:'25px'}}>
{[
{icon:'🎨',title:'Images',href:'/generate/image',desc:'DALL-E, Stable Diffusion'},
{icon:'🎬',title:'Videos',href:'/generate/video',desc:'Text-to-video, Animation'},
{icon:'📝',title:'Text',href:'/generate/text',desc:'Articles, Stories, Code'},
{icon:'🔊',title:'Voice',href:'/generate/voice',desc:'Text-to-speech, Cloning'},
{icon:'📂',title:'Projects',href:'/projects',desc:'Manage your creations'},
{icon:'📊',title:'Analytics',href:'/analytics',desc:'Usage & insights'}
].map((item,i)=>(
<div key={i} onClick={()=>router.push(item.href)} style={{padding:'35px',background:'rgba(255,255,255,0.15)',borderRadius:'20px',cursor:'pointer',transition:'all 0.3s',border:'1px solid rgba(255,255,255,0.2)'}} onMouseOver={e=>{e.currentTarget.style.transform='translateY(-10px)';e.currentTarget.style.background='rgba(255,255,255,0.25)'}} onMouseOut={e=>{e.currentTarget.style.transform='translateY(0)';e.currentTarget.style.background='rgba(255,255,255,0.15)'}}>
<div style={{fontSize:'56px',marginBottom:'15px'}}>{item.icon}</div>
<h3 style={{fontSize:'24px',marginBottom:'10px'}}>{item.title}</h3>
<p style={{fontSize:'14px',opacity:0.8}}>{item.desc}</p>
</div>
))}
</div>
<button onClick={()=>router.push('/login')} style={{marginTop:'50px',padding:'18px 40px',background:'white',color:'#667eea',border:'none',borderRadius:'12px',fontSize:'18px',fontWeight:'700',cursor:'pointer'}}>Get Started Free →</button>
</div>
</div>
)
}
EOF

echo "✅ Landing page created"

# 2. Image Generation
cat > pages/generate/image.js << 'EOF'
import {useState} from 'react'
export default function ImageGen(){
const[prompt,setPrompt]=useState('')
const[url,setUrl]=useState('')
const[loading,setLoading]=useState(false)
const generate=async()=>{
setLoading(true)
try{
const res=await fetch('http://localhost:8000/api/v2/ai/image',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt})})
const data=await res.json()
setUrl(data.url)
}catch(e){alert('Error: '+e.message)}
setLoading(false)
}
return(
<div style={{minHeight:'100vh',background:'#f5f5f5',padding:'50px'}}>
<h1 style={{fontSize:'36px',marginBottom:'30px'}}>🎨 Image Generation</h1>
<textarea value={prompt} onChange={e=>setPrompt(e.target.value)} placeholder="Describe your image..." style={{width:'100%',height:'120px',padding:'15px',fontSize:'16px',borderRadius:'8px',border:'2px solid #ddd',marginBottom:'20px'}}/>
<button onClick={generate} disabled={loading} style={{padding:'15px 40px',background:'#667eea',color:'white',border:'none',borderRadius:'8px',fontSize:'18px',fontWeight:'600',cursor:'pointer'}}>{loading?'Generating...':'Generate Image'}</button>
{url&&<img src={url} style={{marginTop:'30px',maxWidth:'100%',borderRadius:'15px',boxShadow:'0 10px 30px rgba(0,0,0,0.2)'}}/>}
</div>
)
}
EOF

echo "✅ Image generation page created"

# 3. Video Generation
cat > pages/generate/video.js << 'EOF'
import {useState} from 'react'
export default function VideoGen(){
const[prompt,setPrompt]=useState('')
const[url,setUrl]=useState('')
const[loading,setLoading]=useState(false)
const generate=async()=>{
setLoading(true)
try{
const res=await fetch('http://localhost:8000/api/v2/video/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt,duration:4})})
const data=await res.json()
setUrl(data.video_url)
}catch(e){alert('Error: '+e.message)}
setLoading(false)
}
return(
<div style={{minHeight:'100vh',background:'#f5f5f5',padding:'50px'}}>
<h1 style={{fontSize:'36px',marginBottom:'30px'}}>🎬 Video Generation</h1>
<textarea value={prompt} onChange={e=>setPrompt(e.target.value)} placeholder="Describe your video..." style={{width:'100%',height:'120px',padding:'15px',fontSize:'16px',borderRadius:'8px',border:'2px solid #ddd',marginBottom:'20px'}}/>
<button onClick={generate} disabled={loading} style={{padding:'15px 40px',background:'#667eea',color:'white',border:'none',borderRadius:'8px',fontSize:'18px',fontWeight:'600',cursor:'pointer'}}>{loading?'Generating...':'Generate Video'}</button>
{url&&<video src={url} controls style={{marginTop:'30px',maxWidth:'100%',borderRadius:'15px',boxShadow:'0 10px 30px rgba(0,0,0,0.2)'}}/>}
</div>
)
}
EOF

echo "✅ Video generation page created"

# 4. Text Generation
cat > pages/generate/text.js << 'EOF'
import {useState} from 'react'
export default function TextGen(){
const[prompt,setPrompt]=useState('')
const[text,setText]=useState('')
const[loading,setLoading]=useState(false)
const generate=async()=>{
setLoading(true)
try{
const res=await fetch('http://localhost:8000/api/v2/ai/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({messages:[{role:'user',content:prompt}]})})
const data=await res.json()
setText(data.content)
}catch(e){alert('Error: '+e.message)}
setLoading(false)
}
return(
<div style={{minHeight:'100vh',background:'#f5f5f5',padding:'50px'}}>
<h1 style={{fontSize:'36px',marginBottom:'30px'}}>📝 Text Generation</h1>
<textarea value={prompt} onChange={e=>setPrompt(e.target.value)} placeholder="What do you want to write?" style={{width:'100%',height:'120px',padding:'15px',fontSize:'16px',borderRadius:'8px',border:'2px solid #ddd',marginBottom:'20px'}}/>
<button onClick={generate} disabled={loading} style={{padding:'15px 40px',background:'#667eea',color:'white',border:'none',borderRadius:'8px',fontSize:'18px',fontWeight:'600',cursor:'pointer'}}>{loading?'Generating...':'Generate Text'}</button>
{text&&<pre style={{marginTop:'30px',padding:'25px',background:'white',borderRadius:'8px',whiteSpace:'pre-wrap',fontSize:'16px',lineHeight:'1.6'}}>{text}</pre>}
</div>
)
}
EOF

echo "✅ Text generation page created"

# 5. Login Page
cat > pages/login.js << 'EOF'
import {useState} from 'react'
import {useRouter} from 'next/router'
export default function Login(){
const router=useRouter()
const[email,setEmail]=useState('')
const[password,setPassword]=useState('')
const[loading,setLoading]=useState(false)
const login=async()=>{
setLoading(true)
try{
const res=await fetch('http://localhost:8000/api/v2/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email,password})})
const data=await res.json()
if(data.token){localStorage.setItem('token',data.token);router.push('/')}
else alert('Login failed')
}catch(e){alert('Error: '+e.message)}
setLoading(false)
}
return(
<div style={{minHeight:'100vh',background:'linear-gradient(135deg,#667eea,#764ba2)',display:'flex',alignItems:'center',justifyContent:'center'}}>
<div style={{background:'white',padding:'50px',borderRadius:'20px',boxShadow:'0 20px 60px rgba(0,0,0,0.3)',maxWidth:'400px',width:'100%'}}>
<h1 style={{fontSize:'32px',marginBottom:'30px',color:'#333'}}>Sign In</h1>
<input type="email" value={email} onChange={e=>setEmail(e.target.value)} placeholder="Email" style={{width:'100%',padding:'15px',marginBottom:'15px',fontSize:'16px',border:'2px solid #ddd',borderRadius:'8px'}}/>
<input type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="Password" style={{width:'100%',padding:'15px',marginBottom:'25px',fontSize:'16px',border:'2px solid #ddd',borderRadius:'8px'}}/>
<button onClick={login} disabled={loading} style={{width:'100%',padding:'15px',background:'#667eea',color:'white',border:'none',borderRadius:'8px',fontSize:'18px',fontWeight:'600',cursor:'pointer'}}>{loading?'Signing in...':'Sign In'}</button>
</div>
</div>
)
}
EOF

echo "✅ Login page created"

# Restart studio to load new pages
pkill -f "next dev.*3002"
nohup npm run dev -- --port 3002 > /workspace/logs/studio.log 2>&1 &

echo ""
echo "🎉 ALL GALION.STUDIO PAGES CREATED!"
echo ""
echo "Pages available:"
echo "  / - Landing page"
echo "  /generate/image - Image generation"
echo "  /generate/video - Video generation"
echo "  /generate/text - Text generation"
echo "  /login - Authentication"
echo ""
echo "Studio restarting on port 3002..."
echo "Wait 30 seconds then test: curl http://localhost:3002"

