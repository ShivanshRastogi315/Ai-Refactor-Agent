import { useRef, useState, useEffect } from 'react';
import axios from 'axios';
import { DiffEditor } from '@monaco-editor/react';
import './App.css';

function App() {
  const diffEditorRef = useRef(null);
  const fileInputRef = useRef(null);
  
  const defaultCode = `# Paste your legacy code here
def find_duplicates(lst):
    duplicates = []
    for i in range(len(lst)):
        for j in range(i + 1, len(lst)):
            if lst[i] == lst[j] and lst[i] not in duplicates:
                duplicates.append(lst[i])
    return duplicates`;

  const [originalCode, setOriginalCode] = useState(defaultCode);
  const [refactoredCode, setRefactoredCode] = useState('# AI Optimized code will appear here...');
  const [logs, setLogs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const [sourceLanguage, setSourceLanguage] = useState('python');
  const [targetLanguage, setTargetLanguage] = useState('python');

  // --- BATCH PROCESSING STATE ---
  const [taskIds, setTaskIds] = useState([]);
  const [batchStatus, setBatchStatus] = useState(null); 
  const [isPolling, setIsPolling] = useState(false);
  
  // 1. The hard lock to prevent stale closures and ghost intervals
  const pollLock = useRef(false);

  // Fallback dark style for native option menus
  const optionStyle = { backgroundColor: '#1e293b', color: '#fff' };

  function handleEditorMount(editor, monaco) {
    diffEditorRef.current = editor;
  }

  // --- SINGLE FILE REFACTORING ---
  const handleRefactor = async () => {
    setIsLoading(true);
    setLogs(["🔄 Initializing connection to local AI Agent..."]);
    
    const currentCode = diffEditorRef.current 
      ? diffEditorRef.current.getOriginalEditor().getValue() 
      : originalCode;

    try {
      const response = await axios.post('http://localhost:8000/api/refactor', {
        code: currentCode,
        source_lang: sourceLanguage,
        target_lang: targetLanguage
      });
      
      setRefactoredCode(response.data.refactored_code);
      setLogs(response.data.agent_logs);
    } catch (error) {
      setLogs(prev => [...prev, `❌ Network Error: ${error.message}`]);
    } finally {
      setIsLoading(false);
    }
  };

  // --- REPOSITORY BATCH UPLOAD ---
  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    setIsLoading(true);
    setLogs([`📦 Uploading ${file.name} to local workspace...`, "🔄 Extracting and queuing files to Redis..."]);
    setBatchStatus(null); 

    try {
      const response = await axios.post(`http://localhost:8000/api/upload-repo?target_lang=${targetLanguage}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setLogs(prev => [...prev, `✅ ${response.data.message}`]);
      setTaskIds(response.data.task_ids);
      setIsPolling(true); 

    } catch (error) {
      setLogs(prev => [...prev, `❌ Upload Failed: ${error.message}`]);
    } finally {
      setIsLoading(false);
      event.target.value = null; 
    }
  };

  // --- LIVE POLLING FOR PROGRESS BAR (RECURSIVE TIMEOUT FIX) ---
  useEffect(() => {
    pollLock.current = isPolling;

    if (!isPolling || !taskIds || taskIds.length === 0) return;

    let timeoutId;

    const checkStatus = async () => {
        if (!pollLock.current) return; 

        try {
            const response = await axios.post('http://localhost:8000/api/repo-status', taskIds);
            setBatchStatus(response.data);
            
            if (response.data.status === "Completed") {
                setIsPolling(false);
                pollLock.current = false; 
                
                setLogs(prev => {
                    const msg = `🎉 Batch Processing Complete! ${response.data.completed} succeeded, ${response.data.failed} failed.`;
                    if (prev.length > 0 && prev[prev.length - 1] === msg) return prev;
                    return [...prev, msg];
                });
                
                return; 
            }
        } catch (error) {
            console.error("Polling error", error);
            setIsPolling(false);
            pollLock.current = false;
            return; 
        }
        
        if (pollLock.current) {
            timeoutId = setTimeout(checkStatus, 3000);
        }
    };

    checkStatus();

    return () => {
        clearTimeout(timeoutId);
        pollLock.current = false;
    };
    
  }, [isPolling, taskIds]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', backgroundColor: '#0b0f19', color: '#f8fafc' }}>
      
      {/* HEADER CONTROLS (Glassmorphism Effect) */}
      <header style={{ 
        padding: '16px 24px', 
        borderBottom: '1px solid rgba(255,255,255,0.08)', 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        backgroundColor: 'rgba(15, 23, 42, 0.7)',
        backdropFilter: 'blur(12px)',
        zIndex: 10
      }}>
        <div>
          <h2 style={{ margin: '0 0 4px 0', fontSize: '22px', fontWeight: '800', letterSpacing: '-0.5px' }}>
            <span style={{ color: '#10b981' }}>P.R.I.S.M.</span>
          </h2>
          <small style={{ color: '#94a3b8', fontSize: '12px', fontWeight: '500', display: 'block' }}>
            Private Refactoring Intelligence & Sandboxed Machine
          </small>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', backgroundColor: '#1e293b', padding: '6px 12px', borderRadius: '6px', border: '1px solid #334155' }}>
            <label style={{ color: '#cbd5e1', fontSize: '13px', fontWeight: '500' }}>Convert to:</label>
            <select 
              value={targetLanguage} 
              onChange={(e) => setTargetLanguage(e.target.value)}
              /* EXPLICIT BACKGROUND COLOR FIX HERE */
              style={{ backgroundColor: '#1e293b', color: '#fff', border: 'none', outline: 'none', fontSize: '13px', fontWeight: '600', cursor: 'pointer' }}
            >
              <option value="python" style={optionStyle}>Python</option>
              <option value="go" style={optionStyle}>Go</option>
              <option value="cpp" style={optionStyle}>C++</option>
              <option value="java" style={optionStyle}>Java</option>
            </select>
          </div>

          <input type="file" accept=".zip" ref={fileInputRef} style={{ display: 'none' }} onChange={handleFileUpload} />
          
          <button className="btn btn-upload" onClick={() => fileInputRef.current.click()} disabled={isLoading}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
            Upload .zip Repo
          </button>

          <button className="btn btn-refactor" onClick={handleRefactor} disabled={isLoading}>
            {isLoading && taskIds.length === 0 ? (
              <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span className="spinner" style={{ width: '14px', height: '14px', border: '2px solid rgba(255,255,255,0.3)', borderTopColor: '#fff', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></span>
                Processing...
              </span>
            ) : 'Auto-Refactor File'}
          </button>
        </div>
      </header>

      {/* PROGRESS BAR */}
      {batchStatus && (
        <div style={{ padding: '12px 24px', backgroundColor: '#0f172a', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '13px', color: '#cbd5e1', fontWeight: '500' }}>
                <span>Repository Batch Progress</span>
                <span>{batchStatus.completed + batchStatus.failed} / {batchStatus.total} Files Processed</span>
            </div>
            <div style={{ width: '100%', backgroundColor: '#1e293b', borderRadius: '999px', overflow: 'hidden', height: '8px' }}>
                <div style={{ 
                    height: '100%', 
                    backgroundColor: batchStatus.status === 'Completed' ? '#10b981' : '#3b82f6', 
                    width: `${((batchStatus.completed + batchStatus.failed) / batchStatus.total) * 100}%`,
                    transition: 'width 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                    boxShadow: batchStatus.status === 'Completed' ? '0 0 10px rgba(16, 185, 129, 0.5)' : 'none'
                }} />
            </div>
        </div>
      )}

      {/* MAIN DIFF EDITOR AREA */}
      <div style={{ flex: 1, overflow: 'hidden', backgroundColor: '#1e1e1e' }}>
        <DiffEditor
          height="100%" 
          originalLanguage={sourceLanguage}
          modifiedLanguage={targetLanguage}
          original={originalCode} 
          modified={refactoredCode}
          theme="vs-dark" 
          onMount={handleEditorMount}
          options={{ originalEditable: true, readOnly: false, minimap: { enabled: false }, wordWrap: 'on', padding: { top: 16 } }}
        />
      </div>

      {/* EXECUTION LOGS TERMINAL */}
      <div style={{ height: '30vh', backgroundColor: '#0c0c0c', borderTop: '1px solid rgba(255,255,255,0.1)', display: 'flex', flexDirection: 'column' }}>
        
        {/* Terminal Header (Windows 11 Style) */}
        <div style={{ padding: '8px 16px', backgroundColor: '#202020', display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#a1a1aa" strokeWidth="2" strokeLinecap="square" strokeLinejoin="miter">
              <polyline points="4 17 10 11 4 5"></polyline>
              <line x1="12" y1="19" x2="20" y2="19"></line>
            </svg>
            <span style={{ fontSize: '12px', color: '#d4d4d8', fontFamily: '"Segoe UI", sans-serif' }}>Command Prompt - P.R.I.S.M. System Logs</span>
          </div>
          <div style={{ display: 'flex', gap: '14px', alignItems: 'center' }}>
             <span style={{ fontSize: '12px', color: '#a1a1aa', cursor: 'pointer', userSelect: 'none' }}>─</span>
             <span style={{ fontSize: '12px', color: '#a1a1aa', cursor: 'pointer', userSelect: 'none' }}>□</span>
             <span style={{ fontSize: '12px', color: '#a1a1aa', cursor: 'pointer', userSelect: 'none' }}>✕</span>
          </div>
        </div>

        {/* Terminal Body */}
        <div style={{ padding: '16px', overflowY: 'auto', fontFamily: '"Consolas", "Fira Code", monospace', fontSize: '13px', lineHeight: '1.6', flex: 1 }}>
          {logs.map((log, index) => (
            <div key={index} style={{ 
              color: log.includes('❌') ? '#f87171' : log.includes('🎉') || log.includes('✅') ? '#34d399' : '#cccccc',
              marginBottom: '4px'
            }}>
              <span style={{ color: '#555555', marginRight: '12px' }}>{new Date().toLocaleTimeString([], {hour12:false})}</span>
              {log}
            </div>
          ))}
          {/* Blinking Cursor */}
          {isLoading && <div style={{ display: 'inline-block', width: '8px', height: '15px', backgroundColor: '#cccccc', animation: 'blink 1s step-end infinite', marginTop: '4px' }}></div>}
        </div>
      </div>

      {/* DEVELOPER FOOTER */}
      <footer style={{
        padding: '6px 16px',
        backgroundColor: '#050505',
        borderTop: '1px solid #1f2937',
        textAlign: 'right',
        fontSize: '11px',
        color: '#6b7280',
        fontFamily: '"Inter", sans-serif',
        letterSpacing: '0.5px'
      }}>
        Developed by <span style={{ color: '#10b981', fontWeight: '600' }}>Shivansh Rastogi</span>
      </footer>

    </div>
  );
}

export default App;