import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Workflows from './pages/Workflows';
import WorkflowDetail from './pages/WorkflowDetail';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Workflows />} />
        <Route path="/workflow/:name" element={<WorkflowDetail />} />
      </Routes>
    </Router>
  );
}

export default App;
