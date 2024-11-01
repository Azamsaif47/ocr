import React, { useState } from "react";
import { Upload, Button, Table, message } from "antd";
import { UploadOutlined, DownloadOutlined } from "@ant-design/icons";
import axios from "axios";
import ExcelJS from "exceljs";
import { saveAs } from "file-saver";
import "./UploadExamSheets.css"; // Import custom CSS file

const UploadExamSheets = () => {
  const [fileList, setFileList] = useState([]);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    const formData = new FormData();
    fileList.forEach((file) => {
      const fileToAppend = file.originFileObj || file;
      if (fileToAppend instanceof File) {
        formData.append("files", fileToAppend);
      }
    });

    setLoading(true);
    try {
      const response = await axios.post("http://127.0.0.1:8000/process-answer-sheets/", formData);
      const processedResults = response.data.results.map((result) => ({
        filename: result.filename,
        totalQuestions: result["Total Questions"] || 0,
        correctAnswers: result["Correct Answers"] || 0,
        incorrectAnswers: result["Incorrect Answers"] || 0,
        unansweredQuestions: result["Unanswered Questions"] || 0,
        percentage: result["Percentage"] || 0,
      }));

      setResults(processedResults);
      message.success("Exam sheets processed successfully!");
    } catch (error) {
      console.error("Upload Error:", error.response?.data || error.message);
      message.error(
        `Failed to process exam sheets: ${
          error.response?.data?.detail || error.response?.data?.error || "Please try again."
        }`
      );
    } finally {
      setLoading(false);
    }
  };

  const exportToExcel = () => {
    if (results.length === 0) {
      message.warning("No results to export.");
      return;
    }

    const workbook = new ExcelJS.Workbook();
    const worksheet = workbook.addWorksheet("Results");

    worksheet.columns = [
      { header: "File Name", key: "filename", width: 20 },
      { header: "Total Questions", key: "totalQuestions", width: 20 },
      { header: "Correct Answers", key: "correctAnswers", width: 20 },
      { header: "Incorrect Answers", key: "incorrectAnswers", width: 20 },
      { header: "Unanswered Questions", key: "unansweredQuestions", width: 20 },
      { header: "Percentage", key: "percentage", width: 20 },
    ];

    results.forEach((result) => {
      worksheet.addRow(result);
    });

    workbook.xlsx.writeBuffer().then((buffer) => {
      const blob = new Blob([buffer], { type: "application/octet-stream" });
      saveAs(blob, "Exam_Results.xlsx");
    });
  };

  const columns = [
    { title: "File Name", dataIndex: "filename", key: "filename" },
    { title: "Total Questions", dataIndex: "totalQuestions", key: "totalQuestions" },
    { title: "Correct Answers", dataIndex: "correctAnswers", key: "correctAnswers" },
    { title: "Incorrect Answers", dataIndex: "incorrectAnswers", key: "incorrectAnswers" },
    { title: "Unanswered Questions", dataIndex: "unansweredQuestions", key: "unansweredQuestions" },
    { title: "Percentage", dataIndex: "percentage", key: "percentage" },
  ];

  return (
    <div className="upload-exam-sheets-container">
      <h2>Upload Exam Sheets</h2>
      <div className="file-upload-section">
        <Upload
          multiple
          beforeUpload={(file) => {
            setFileList((prevList) => [...prevList, file]);
            return false;
          }}
          onRemove={(file) => {
            setFileList((prevList) => prevList.filter((item) => item.uid !== file.uid));
          }}
          fileList={fileList}
        >
          <Button icon={<UploadOutlined />}>Select Exam Sheets</Button>
        </Upload>
      </div>
      <Button
        type="primary"
        onClick={handleUpload}
        loading={loading}
        style={{ marginTop: 16 }}
        disabled={fileList.length === 0}
      >
        Upload and Process
      </Button>
      <Button
        icon={<DownloadOutlined />}
        onClick={exportToExcel}
        style={{ marginTop: 16, marginLeft: 8 }}
        disabled={results.length === 0}
      >
        Export Results to Excel
      </Button>
      <Table
        columns={columns}
        dataSource={results}
        rowKey="filename"
        style={{ marginTop: 24 }}
      />
    </div>
  );
};

export default UploadExamSheets;
