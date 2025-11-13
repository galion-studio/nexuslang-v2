// Web IDE Page for developer.galion.app
import Head from 'next/head'
import CodeEditor from '../components/CodeEditor'

export default function IDEPage() {
  return (
    <div style={{padding: '20px'}}>
      <Head>
        <title>Web IDE - NexusLang</title>
      </Head>
      
      <h1>🚀 NexusLang Web IDE</h1>
      <p style={{color: '#666'}}>Write and execute NexusLang code in your browser</p>
      
      <div style={{marginTop: '30px'}}>
        <CodeEditor />
      </div>
      
      <div style={{marginTop: '30px', padding: '20px', backgroundColor: '#f5f5f5', borderRadius: '8px'}}>
        <h3>Quick Tips:</h3>
        <ul>
          <li>Press the Run button to execute your code</li>
          <li>Each execution costs 0.01 credits</li>
          <li>Code executes in a secure sandbox</li>
          <li>Timeout: 30 seconds max</li>
        </ul>
      </div>
    </div>
  )
}

