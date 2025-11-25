import { Routes, Route } from 'react-router-dom';
import UserList from '../components/users/UserList';
import UserForm from '../components/users/UserForm';

const UsersPage = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <Routes>
        <Route index element={<UserList />} />
        <Route path="new" element={<UserForm />} />
        <Route path=":id/edit" element={<UserForm />} />
      </Routes>
    </div>
  );
};

export default UsersPage;
