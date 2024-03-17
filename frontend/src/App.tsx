import React, { useState, ChangeEvent } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import "./App.css";

export default function App() {
  const [result, setResult] = useState<string>("");
  const [file, setFile] = useState<File | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<boolean>(false);
  const [query, setQuery] = useState<string>("");
  const [showUploadSuccessModal, setShowUploadSuccessModal] = useState<boolean>(false);
  const [fileUploadResult, setFileUploadResult] = useState<string>("");

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setFile(event.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      setUploadSuccess(true); // File uploaded successfully
      setFileUploadResult(data.result); // File uploaded successfully
      setShowUploadSuccessModal(true); // Show upload success modal
    } catch (error) {
      console.error("Error", error);
      alert("Error uploading file. Please try again.");
    }
  };

  const handlePredict = async () => {
    if (!file || !query) return;
  
    try {
      const response = await fetch(`http://localhost:8000/predict?query=${encodeURIComponent(query)}`, {
        method: "POST",
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json' // Set content type if needed
        },
        body: JSON.stringify({}) // Empty body, as data is sent in URL params
      });
      const data = await response.json();
      setResult(data.result);
    } catch (error) {
      console.error("Error", error);
      setResult("Error occurred during prediction.");
    }
  };

  return (
    <div className="container mt-5">
      <div className="row justify-content-center">
        <div className="col-md-6">
          <div className="appBlock">
            <input
              type="file"
              id="file"
              name="file"
              accept=".pdf,.docx,.txt,.csv"
              onChange={handleFileChange}
              className="fileInput form-control"
            />
            <br />
            <button className="uploadBtn btn btn-primary" onClick={handleUpload} disabled={!file}>
              Upload File
            </button>
            <br />
            {uploadSuccess && (
              <>
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="form-control mt-3"
                  placeholder="Ask a question..."
                />
                <br />
                <button className="predictBtn btn btn-success" onClick={handlePredict}>
                  Ask
                </button>
              </>
            )}
            <p className="resultOutput">Result: {result}</p>
          </div>
        </div>
      </div>

      {/* Upload Success Modal */}
      <div className="modal" tabIndex={-1} role="dialog" style={{ display: showUploadSuccessModal ? "block" : "none" }}>
        <div className="modal-dialog" role="document">
          <div className="modal-content">
            <div className="modal-header">
              <h5 className="modal-title">Upload Success</h5>
              <button type="button" className="close" onClick={() => setShowUploadSuccessModal(false)}>
                <span aria-hidden="true">&times;</span>
              </button>
            </div>
            <div className="modal-body">
            <p>{fileUploadResult}</p>
            </div>
            <div className="modal-footer">
              <button type="button" className="btn btn-primary" onClick={() => setShowUploadSuccessModal(false)}>
                Close
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
