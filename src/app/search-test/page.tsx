'use client';

export default function SearchTest() {
  // #region agent log
  try{fetch('http://127.0.0.1:7242/ingest/922e0c9a-fc2e-4baa-9d6c-cdb2a1ae398a',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'search-test/page.tsx:5',message:'SearchTest minimal render',data:{},timestamp:Date.now(),sessionId:'debug-session',runId:'run2',hypothesisId:'I'})}).catch(()=>{});}catch(e){}
  // #endregion

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold">Minimal Test Page</h1>
      <p>If you can see this, the issue is with the full search page complexity.</p>
    </div>
  );
}

